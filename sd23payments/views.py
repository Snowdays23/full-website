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

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView

from sd23payments.models import Order
from sd23payments.utils import create_order, capture_payment

import stripe

stripe.api_key = settings.STRIPE_SECRET_API_KEY


class CreateStripeCheckout(View):
    def post(self, request, sd_order_id=None):
        try:
            order = Order.objects.get(sd_order_id=sd_order_id)
        except Order.DoesNotExist:
            return HttpResponse(204)
        
        if not order.is_eligible_for_payment():
            return HttpResponse(204)

        amount = order.amount
                
        price = stripe.Price.create(
            unit_amount=18000,
            currency="eur",
            product_data={
                "name": "SnowDays Ticket"
            }
        )
        session = stripe.checkout.Session.create(
            success_url=settings.STRIPE_CHECKOUT_SUCCESS_URL % sd_order_id,
            cancel_url=settings.STRIPE_CHECKOUT_CANCEL_URL % sd_order_id,
            line_items=[
                {
                    "price": price.id,
                    "quantity": 1
                }
            ],
            mode="payment"
        )
        print(session.id)

        return redirect(session.url)


class StripeCheckoutCompleted(View):
    def get(self, request, **kwargs):
        print(request.GET)
        print(kwargs)
        return HttpResponse("OK")