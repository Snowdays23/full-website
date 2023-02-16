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
    GetParticipantByBraceletId, 
    AssignBraceletToParticipant,
    CheckInParticipantOrPartyBeast,
    EventViewSet
)

urlpatterns = [
    path('participant/<str:uid>', GetParticipantByBraceletId.as_view(), name="get-participant-by-uid"),
    path('participant/<int:pk>/<str:uid>', AssignBraceletToParticipant.as_view(), name="assign-bracelet-to-participant"),
    path('event/<str:event_slug>/check-in/<str:bracelet_uid>', CheckInParticipantOrPartyBeast.as_view(), name="check-in-to-event"),
    path('events', EventViewSet.as_view({
        "get": "list",
        "post": "create"
    }), name="check-in-to-event"),
]