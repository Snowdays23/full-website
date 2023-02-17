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

import re

from django.conf import settings
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from rest_framework import status, viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from snowdays23.models import Participant, PartyBeast
from snowdays23.serializers import ParticipantSerializer

from sd23log.models import Event, CheckIn
from sd23log.serializers import NewEventSerializer, EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    
    def get_serializer_class(self):
        if not hasattr(self, 'action'):
            return EventSerializer
        if self.action == "create":
            return NewEventSerializer
        return EventSerializer

    def retrieve(self, request, slug=None):
        event = get_object_or_404(self.get_queryset(), slug=slug)
        serializer = self.get_serializer_class()(event)
        return Response(serializer.data)

    def list(self, request, **kwargs):
        # if not request.user.is_authenticated or not request.user.is_staff:
        #     return Response(
        #         [], 
        #         status=status.HTTP_401_UNAUTHORIZED
        #     )
        return super().list(self, request, **kwargs)


class CheckInParticipantOrPartyBeast(APIView):
    def post(self, request, event_slug=None, bracelet_uid=None):
        if not event_slug or not bracelet_uid:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        participant = None
        party_beast = None
        try:
            event = get_object_or_404(Event, slug=event_slug)
            if Participant.objects.filter(bracelet_id=bracelet_uid).exists():
                participant = Participant.objects.get(bracelet_id=bracelet_uid)
            elif PartyBeast.objects.filter(bracelet_id=bracelet_uid).exists():
                party_beast = PartyBeast.objects.get(bracelet_id=bracelet_uid)
            else:
                raise
        except:
            return Response({
                "detail": _("Event or participant/partybeast not found")
            }, status=status.HTTP_404_NOT_FOUND)

        if party_beast and event.only_participants:
            return Response({
                "detail": _("Event is participants only!")
            }, status=status.HTTP_400_BAD_REQUEST)

        if CheckIn.objects.filter(
            event=event, participant=participant
        ).exists() or CheckIn.objects.filter(
            event=event, party_beast=party_beast
        ).exists():
            return Response({
                "detail": _("Participant/partybeast already checked-in!")
            }, status=status.HTTP_400_BAD_REQUEST)

        CheckIn.objects.create(
            event=event,
            participant=participant or None,
            party_beast=party_beast or None
        )
        return Response({
            "detail": _("Checked-in successfully!")
        }, status=status.HTTP_200_OK)


class GetParticipantByBraceletId(APIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    def get(self, request, uid=None):
        if not uid:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        participant = get_object_or_404(Participant, bracelet_id=uid)
        return Response(self.serializer_class(participant).data)


class AssignBraceletToParticipant(APIView):
    def post(self, request, pk=None, uid=None):
        if not pk or not uid:
            return Response({
                "detail": _("Missing parameters")
            }, status=status.HTTP_400_BAD_REQUEST)

        participant = get_object_or_404(Participant, pk=pk)
        
        if not re.match(settings.BRACELET_ID_REGEX, uid):
            return Response({
                "detail": _("Invalid UID")
            }, status=status.HTTP_400_BAD_REQUEST)

        another = Participant.objects.filter(bracelet_id=uid)
        if another.exists():
            return Response({
                "detail": _("UID already assigned to another participant")
            }, status=status.HTTP_400_BAD_REQUEST)

        participant.bracelet_id = uid
        participant.save()

        return Response({
            "detail": _("Bracelet assigned successfully")
        }, status=status.HTTP_200_OK)