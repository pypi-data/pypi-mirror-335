# Copyright (C) 2017-2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
from typing import Any, Dict, Optional

from swh.core import config
from swh.deposit import __version__
from swh.model.model import MetadataAuthority, MetadataAuthorityType, MetadataFetcher

# IRIs (Internationalized Resource identifier) sword 2.0 specified
EDIT_IRI = "edit_iri"
SE_IRI = "se_iri"
EM_IRI = "em_iri"
CONT_FILE_IRI = "cont_file_iri"
SD_IRI = "servicedocument"
COL_IRI = "upload"
STATE_IRI = "state_iri"
PRIVATE_GET_RAW_CONTENT = "private-download"
PRIVATE_PUT_DEPOSIT = "private-update"
PRIVATE_GET_DEPOSIT_METADATA = "private-read"
PRIVATE_LIST_DEPOSITS = "private-deposit-list"
PRIVATE_LIST_DEPOSITS_DATATABLES = "private-deposit-list-datatables"
PRIVATE_GET_RELEASES = "private-releases"
PRIVATE_GET_UPLOAD_URLS = "private-upload-urls"

ARCHIVE_KEY = "archive"
RAW_METADATA_KEY = "raw-metadata"

ARCHIVE_TYPE = "archive"
METADATA_TYPE = "metadata"

AUTHORIZED_PLATFORMS = ["development", "production", "testing"]

DEPOSIT_STATUS_REJECTED = "rejected"
DEPOSIT_STATUS_PARTIAL = "partial"
DEPOSIT_STATUS_DEPOSITED = "deposited"
DEPOSIT_STATUS_VERIFIED = "verified"
DEPOSIT_STATUS_LOAD_SUCCESS = "done"
DEPOSIT_STATUS_LOAD_FAILURE = "failed"

# Release author for deposit
SWH_PERSON = {
    "name": "Software Heritage",
    "fullname": "Software Heritage",
    "email": "robot@softwareheritage.org",
}


DEFAULT_CONFIG = {
    "max_upload_size": 209715200,
    "checks": True,
}


def setup_django_for(platform: Optional[str] = None, config_file: Optional[str] = None):
    """Setup function for command line tools (e.g. swh.deposit.create_user) to
    initialize the needed db access.

    Note:
        Do not import any django related module prior to this function
        call. Otherwise, this will raise a django.core.exceptions.ImproperlyConfigured
        error message.

    Args:
        platform: the platform to use when running program (e.g. cli, ...)
        config_file: Extra configuration file (typically for the production platform)

    Raises:
        ValueError in case of wrong platform inputs

    """
    if platform is not None:
        if platform not in AUTHORIZED_PLATFORMS:
            raise ValueError(f"Platform should be one of {AUTHORIZED_PLATFORMS}")
        if "DJANGO_SETTINGS_MODULE" not in os.environ:
            os.environ["DJANGO_SETTINGS_MODULE"] = f"swh.deposit.settings.{platform}"

    if config_file:
        # Hack to set the environment variable which in some cases is required (e.g.
        # production)
        os.environ.setdefault("SWH_CONFIG_FILENAME", config_file)

    from django import setup

    setup()


class APIConfig:
    """API Configuration centralized class. This loads explicitly the configuration file out
    of the SWH_CONFIG_FILENAME environment variable.

    """

    def __init__(self):
        from swh.scheduler import get_scheduler
        from swh.scheduler.interface import SchedulerInterface
        from swh.storage import get_storage
        from swh.storage.interface import StorageInterface

        self.config: Dict[str, Any] = config.load_from_envvar(DEFAULT_CONFIG)
        self.scheduler: SchedulerInterface = get_scheduler(**self.config["scheduler"])
        self.tool = {
            "name": "swh-deposit",
            "version": __version__,
            "configuration": {"sword_version": "2"},
        }
        self.storage: StorageInterface = get_storage(**self.config["storage"])
        self.storage_metadata: StorageInterface = get_storage(
            **self.config["storage_metadata"]
        )

    def swh_deposit_authority(self):
        return MetadataAuthority(
            type=MetadataAuthorityType.REGISTRY,
            url=self.config["swh_authority_url"],
        )

    def swh_deposit_fetcher(self):
        return MetadataFetcher(
            name=self.tool["name"],
            version=self.tool["version"],
        )
