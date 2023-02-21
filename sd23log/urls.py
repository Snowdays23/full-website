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

from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from sd23log.views import (
    GetParticipantOrPartyBeastByBraceletId,
    AssignBraceletToParticipant,
    AssignBraceletToPartyBeast,
    CheckInParticipantOrPartyBeast,
    EventViewSet
)

urlpatterns = [
    path('people/<str:uid>', GetParticipantOrPartyBeastByBraceletId.as_view(), name="get-participant-or-party-beast-by-uid"),
    path('participant/<int:pk>/<str:uid>', AssignBraceletToParticipant.as_view(), name="assign-bracelet-to-participant"),
    path('partybeast/<int:pk>/<str:uid>', AssignBraceletToPartyBeast.as_view(), name="assign-bracelet-to-party-beast"),
    path('event/<str:event_slug>/check-in/<str:bracelet_uid>', CheckInParticipantOrPartyBeast.as_view(), name="check-in-to-event"),
    path('events', EventViewSet.as_view({
        "get": "list",
        "post": "create"
    }), name="events"),
    path('event/<str:slug>', EventViewSet.as_view({
        "get": "retrieve"
    }), name="event-by-slug")
]