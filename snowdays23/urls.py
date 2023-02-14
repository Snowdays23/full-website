# This file is part of the Snowdays23 project
# Copyright (C) 2022 Snowdays
# Author: Andrea Esposito <aespositox@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""snowdays23 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import urllib.parse

from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.shortcuts import render, redirect, reverse
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from snowdays23.views import (
    ParticipantViewSet,
    PartyBeastViewSet
)


def serve_react(request):
    return render(request, "index.html")

def redirect_error(code, **kwargs):
    return redirect("%s?%s" % (reverse("error"), urllib.parse.urlencode({
        "code": code,
        **kwargs
    })))


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/participants', ParticipantViewSet.as_view({
        "get": "list",
        "post": "create"
    }), name="all_parts"),
    path('api/partybeasts', PartyBeastViewSet.as_view({
        "get": "list",
        "post": "create"
    }), name="all_party_beasts"),
    path('api/payments/', include('sd23payments.urls')),
    path('api/track/', include('sd23log.urls')),

    path('not-found', serve_react, name="not-found"),
    path('error', serve_react, name="error"),
    re_path(r"^$", serve_react),
    re_path(r"^(?:.*)/?$", serve_react),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()