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

from django.conf import settings
from django.shortcuts import render

from rest_framework import status, viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from snowdays23.models import Participant
from snowdays23.serializers import ParticipantSerializer


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