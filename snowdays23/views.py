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
import secrets

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from rest_framework import status, viewsets
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from post_office import mail

from snowdays23.models import Participant, PartyBeast
from snowdays23.serializers import ParticipantSerializer, NewParticipantSerializer, PartyBeastSerializer

from sd23payments.models import Order, BillableItem


class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    
    def get_serializer_class(self):
        if not hasattr(self, 'action'):
            return ParticipantSerializer
        if self.action == "create":
            return NewParticipantSerializer
        return ParticipantSerializer

    # def list(self, request, **kwargs):
    #     if not request.user.is_authenticated or not request.user.is_staff:
    #         return Response(
    #             [], 
    #             status=status.HTTP_401_UNAUTHORIZED
    #         )
    #     return super().list(self, request, **kwargs)

    def perform_create(self, serializer):
        participant = serializer.save()

        # If previous order(s) associated to this participant exist(s), they must be
        # deleted: user has signed up again (maybe payment link has expired) 
        orders = Order.objects.filter(participant=participant)
        if orders.exists():
            orders.delete()

        # If a party beast with the same email exists, it must be
        # deleted: user has signed up again (maybe payment link has expired)
        PartyBeast.objects.filter(user__email__iexact=participant.user.email).delete()

        if participant.internal and participant.internal_type.name == "alumnus":
            ticket = BillableItem.objects.get(slug="alumnus-ticket")
        elif participant.internal:
            ticket = BillableItem.objects.get(slug="internal-ticket")
        else:
            ticket = BillableItem.objects.get(slug="ticket")
        order = Order.objects.create(
            participant=participant
        )
        order.items.add(ticket)

        if participant.internal:
            mail.send(
                participant.user.email,
                "Snowdays <noreply@snowdays.it>",
                template="internals-form-confirmation",
                context={
                    'host': settings.HOST,
                    'participant': participant,
                    'checkout_url': reverse("stripe-checkout", kwargs={
                        "sd_order_id": order.sd_order_id
                    }, current_app="sd23payments")
                },
                priority='now'
            )
        else:
            mail.send(
                participant.user.email,
                "Snowdays <noreply@snowdays.it>",
                template="form-confirmation",
                context={
                    'host': settings.HOST,
                    'participant': participant,
                    'checkout_url': reverse("stripe-checkout", kwargs={
                        "sd_order_id": order.sd_order_id
                    }, current_app="sd23payments")
                },
                priority='now'
            )


class PartyBeastViewSet(viewsets.ModelViewSet):
    queryset = PartyBeast.objects.all()
    serializer_class = PartyBeastSerializer
    
    def list(self, request, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                [], 
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().list(self, request, **kwargs)

    def perform_create(self, serializer):
        party_beast = serializer.save()

        # If previous order(s) associated to this party beast exist(s), they must be
        # deleted: user has signed up again (maybe payment link has expired) 
        orders = Order.objects.filter(party_beast=party_beast)
        if orders.exists():
            orders.delete()

        # If a participant with the same email exists, it must be
        # deleted: user has signed up again (maybe payment link has expired)
        Participant.objects.filter(user__email__iexact=party_beast.user.email).delete()

        ticket = BillableItem.objects.get(slug="party-beast-pack")
        order = Order.objects.create(
            party_beast=party_beast
        )
        order.items.add(ticket)

        mail.send(
            party_beast.user.email,
            "Snowdays <noreply@snowdays.it>",
            template="party-form-confirmation",
            context={
                'host': settings.HOST,
                'party_beast': party_beast,
                'checkout_url': reverse("stripe-checkout", kwargs={
                    "sd_order_id": order.sd_order_id
                }, current_app="sd23payments")
            },
            priority='now'
        )