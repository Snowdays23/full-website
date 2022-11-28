# This file is part of the SnowDays23 project
# Copyright (C) 2022 SnowDays
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
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets

from snowdays23.models import Participant
from snowdays23.serializers import ParticipantSerializer


class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer


class GetParticipantByBraceletId(APIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    def get(self, request, uid=None):
        if not uid:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        participant = Participant.objects.filter(bracelet_id=uid)
        if participant.exists():
            return Response(self.serializer_class(participant.first()).data)
        return Response(status=status.HTTP_404_NOT_FOUND)


class AssignBraceletToParticipant(APIView):
    def post(self, request, pk=None, uid=None):
        if not pk or not uid:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            participant = Participant.objects.get(pk=pk)
        except Participant.NotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if not re.match(settings.BRACELET_ID_REGEX, uid):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        another = Participant.objects.filter(bracelet_id=uid)
        if another.exists():
            return Response({
                "detail": _("UID already assigned to another participant")
            }, status=status.HTTP_400_BAD_REQUEST)

        participant.bracelet_id = uid
        participant.save()

        return Response(status=status.HTTP_200_OK)