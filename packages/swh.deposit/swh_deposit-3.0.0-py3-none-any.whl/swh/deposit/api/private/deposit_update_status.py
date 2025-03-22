# Copyright (C) 2017-2025 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from rest_framework.parsers import JSONParser

from swh.deposit.api.common import APIPut, ParsedRequestHeaders
from swh.deposit.api.private import APIPrivateView
from swh.deposit.errors import BAD_REQUEST, DepositError
from swh.deposit.models import (
    DEPOSIT_STATUS_DETAIL,
    DEPOSIT_STATUS_LOAD_SUCCESS,
    DEPOSIT_STATUS_VERIFIED,
    Deposit,
)
from swh.model.hashutil import hash_to_bytes
from swh.model.swhids import CoreSWHID, ObjectType, QualifiedSWHID
from swh.scheduler.utils import create_oneshot_task

MANDATORY_KEYS = ["origin_url", "release_id", "directory_id", "snapshot_id"]


class APIUpdateStatus(APIPrivateView, APIPut):
    """Deposit request class to update the deposit's status.

    HTTP verbs supported: PUT

    """

    parser_classes = (JSONParser,)

    def additional_checks(
        self, request, headers: ParsedRequestHeaders, collection_name, deposit=None
    ):
        """Enrich existing checks to the default ones.

        New checks:
        - Ensure the status is provided
        - Ensure it exists
        - no missing information on load success update

        """
        data = request.data
        status = data.get("status")
        if not status:
            msg = "The status key is mandatory with possible values %s" % list(
                DEPOSIT_STATUS_DETAIL.keys()
            )
            raise DepositError(BAD_REQUEST, msg)

        if status not in DEPOSIT_STATUS_DETAIL:
            msg = "Possible status in %s" % list(DEPOSIT_STATUS_DETAIL.keys())
            raise DepositError(BAD_REQUEST, msg)

        if status == DEPOSIT_STATUS_LOAD_SUCCESS:
            missing_keys = []
            for key in MANDATORY_KEYS:
                value = data.get(key)
                if value is None:
                    missing_keys.append(key)

            if missing_keys:
                msg = (
                    f"Updating deposit status to {status}"
                    f" requires information {','.join(missing_keys)}"
                )
                raise DepositError(BAD_REQUEST, msg)

        return {}

    def process_put(
        self,
        request,
        headers: ParsedRequestHeaders,
        collection_name: str,
        deposit: Deposit,
    ) -> None:
        """Update the deposit with status, SWHIDs and release infos.

        Returns:
            204 No content
            400 Bad request if checks fail
        """
        data = request.data

        status = data["status"]
        deposit.status = status
        if status == DEPOSIT_STATUS_LOAD_SUCCESS:
            origin_url = data["origin_url"]
            directory_id = data["directory_id"]
            release_id = data["release_id"]
            dir_id = CoreSWHID(
                object_type=ObjectType.DIRECTORY, object_id=hash_to_bytes(directory_id)
            )
            snp_id = CoreSWHID(
                object_type=ObjectType.SNAPSHOT,
                object_id=hash_to_bytes(data["snapshot_id"]),
            )
            rel_id = CoreSWHID(
                object_type=ObjectType.RELEASE, object_id=hash_to_bytes(release_id)
            )

            deposit.swhid = str(dir_id)
            # new id with contextual information
            deposit.swhid_context = str(
                QualifiedSWHID(
                    object_type=ObjectType.DIRECTORY,
                    object_id=hash_to_bytes(directory_id),
                    origin=origin_url,
                    visit=snp_id,
                    anchor=rel_id,
                    path="/",
                )
            )
        elif (
            status == DEPOSIT_STATUS_VERIFIED
            and not deposit.load_task_id
            and self.config["checks"]
        ):
            # Deposit ok, then we schedule the deposit loading task (if not already done)
            url = deposit.origin_url
            task = create_oneshot_task(
                "load-deposit", url=url, deposit_id=deposit.id, retries_left=3
            )
            load_task_id = self.scheduler.create_tasks([task])[0].id
            deposit.load_task_id = str(load_task_id)

        if "status_detail" in data:
            deposit.status_detail = data["status_detail"]

        deposit.save()
