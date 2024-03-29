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
from snowdays23.serializers import ParticipantSerializer, PartyBeastSerializer, ParticipantOrPartyBeastSerializer

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

    def delete(self, request, slug=None):
        event = get_object_or_404(self.get_queryset(), slug=slug)
        event.delete()
        return Response({
            "detail": _("Checked-in successfully!")
        }, status=status.HTTP_200_OK)

    def list(self, request, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                [], 
                status=status.HTTP_401_UNAUTHORIZED
            )
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
                "detail": _("Person not found")
            }, status=status.HTTP_404_NOT_FOUND)

        if party_beast and event.only_participants:
            return Response({
                "detail": _("Event is participants only!")
            }, status=status.HTTP_400_BAD_REQUEST)

        if CheckIn.objects.filter(
            event=event, participant=participant, participant__isnull=False
        ).exists() or CheckIn.objects.filter(
            event=event, party_beast=party_beast, party_beast__isnull=False
        ).exists():
            return Response({
                "detail": _("Already checked-in!")
            }, status=status.HTTP_400_BAD_REQUEST)

        CheckIn.objects.create(
            event=event,
            participant=participant or None,
            party_beast=party_beast or None
        )
        return Response({
            "detail": _("Checked-in successfully!")
        }, status=status.HTTP_200_OK)


class GetParticipantOrPartyBeastByBraceletId(APIView):
    serializer_class = ParticipantOrPartyBeastSerializer

    def get(self, request, uid=None):
        if not uid:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        participant = Participant.objects.filter(bracelet_id=uid)
        party_beast = PartyBeast.objects.filter(bracelet_id=uid)
        if participant.exists():
            return Response(self.serializer_class({
                "participant": participant.first(),
                "party_beast": None
            }).data)
        elif party_beast.exists():
            return Response(self.serializer_class({
                "participant": None,
                "party_beast": party_beast.first()
            }).data)
        return Response({
            "detail": _("No participant or party beast found with this bracelet")
        }, status=status.HTTP_404_NOT_FOUND)


class AssignBraceletToParticipant(APIView):
    def post(self, request, pk=None, uid=None):
        if pk == None or uid == None:
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
                "detail": _("Bracelet already assigned to another participant")
            }, status=status.HTTP_400_BAD_REQUEST)

        another = PartyBeast.objects.filter(bracelet_id=uid)
        if another.exists():
            return Response({
                "detail": _("Bracelet already assigned to another party beast")
            }, status=status.HTTP_400_BAD_REQUEST)

        participant.bracelet_id = uid
        participant.save()

        return Response({
            "detail": _("Bracelet assigned successfully")
        }, status=status.HTTP_200_OK)


class AssignBraceletToPartyBeast(APIView):
    def post(self, request, pk=None, uid=None):
        if pk == None or uid == None:
            return Response({
                "detail": _("Missing parameters")
            }, status=status.HTTP_400_BAD_REQUEST)

        party_beast = get_object_or_404(PartyBeast, pk=pk)
        
        if not re.match(settings.BRACELET_ID_REGEX, uid):
            return Response({
                "detail": _("Invalid UID")
            }, status=status.HTTP_400_BAD_REQUEST)

        another = Participant.objects.filter(bracelet_id=uid)
        if another.exists():
            return Response({
                "detail": _("Bracelet already assigned to another participant")
            }, status=status.HTTP_400_BAD_REQUEST)

        another = PartyBeast.objects.filter(bracelet_id=uid)
        if another.exists():
            return Response({
                "detail": _("UID already assigned to another party beast")
            }, status=status.HTTP_400_BAD_REQUEST)

        party_beast.bracelet_id = uid
        party_beast.save()

        return Response({
            "detail": _("Bracelet assigned successfully")
        }, status=status.HTTP_200_OK)