# Copyright (C) 2017-2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

"""SWH's main deposit URL Configuration"""
from __future__ import annotations

from typing import Sequence, Union

from django.conf import settings
from django.conf.urls import include
from django.shortcuts import render
from django.urls import re_path as url
from django.views.generic.base import RedirectView
from django.views.static import serve
from rest_framework.urlpatterns import format_suffix_patterns

try:
    from django.urls import URLPattern, URLResolver
except ImportError:
    # retro-compatibility workaround, django 1.11.29 [1] does not expose the previous
    # module, so we fallback to no typing for such version.
    # [1] django debian stable version: 1:1.11.29-1~deb10u1
    pass


favicon_view = RedirectView.as_view(
    url="/static/img/icons/swh-logo-32x32.png", permanent=True
)


def default_view(req, format=None):
    return render(req, "homepage.html")


urlpatterns: Sequence[Union[URLPattern, URLResolver]]
urlpatterns = format_suffix_patterns(
    [
        url(r"^favicon\.ico$", favicon_view),
        url(r"^1/", include("swh.deposit.api.urls")),
        url(r"^1/private/", include("swh.deposit.api.private.urls")),
        url(r"^$", default_view, name="home"),
    ]
)

if "AzureStorage" not in settings.STORAGES["default"]["BACKEND"]:
    # to serve uploaded tarballs when no azure storage backend is configured,
    # typically in docker or with development/test settings
    urlpatterns.append(
        url(
            rf"^{settings.MEDIA_URL.rstrip('/').split('/')[-1]}/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        )
    )
