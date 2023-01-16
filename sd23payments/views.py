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
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse

from rest_framework import status
from rest_framework.views import APIView
from post_office import mail

from sd23payments.models import Order
from snowdays23.urls import redirect_error

import stripe
import datetime
import urllib.parse

stripe.api_key = settings.STRIPE_SECRET_API_KEY


class CreateStripeCheckout(View):
    def get(self, request, sd_order_id=None):
        try:
            order = Order.objects.get(sd_order_id=sd_order_id)
        except Order.DoesNotExist:
            return redirect("not-found")

        if order.participant.internal and order.participant.internal_type.name != "alumnus":
            if datetime.datetime.now(tz=order.created.tzinfo) - order.created > settings.INTERNALS_EXPIRATION_DELTA:
                return redirect_error(454)

        if order.status == "paid":
            return redirect("not-found")
        
        if order.stripe_order_id:
            if order.participant.internal:
                try:
                    session = stripe.checkout.Session.retrieve(order.stripe_order_id)
                    return redirect(session.url)
                except:
                    # Session could not be retrieved: create a new one
                    pass
            multiple_sessions = True
        else:
            multiple_sessions = False

        items = [{
            "price": item.id,
            "quantity": 1
        } for item in [stripe.Price.create(
            unit_amount=order_item.price,
            currency="eur",
            product_data={
                "name": order_item.name
            }
        ) for order_item in order.items.all()]]

        if order.participant.internal and order.participant.internal_type.name != "alumnus":
            session = stripe.checkout.Session.create(
                success_url=settings.HOST + reverse("stripe-success", kwargs={
                    "sd_order_id": order.sd_order_id
                }),
                cancel_url=settings.HOST + reverse("stripe-cancel", kwargs={
                    "sd_order_id": order.sd_order_id
                }),
                line_items=items,
                mode="payment",
                payment_intent_data={
                    "capture_method": "manual"
                },
                expires_at=datetime.datetime.now() + settings.INTERNALS_EXPIRATION_DELTA
            )
        else:
            session = stripe.checkout.Session.create(
                success_url=settings.HOST + reverse("stripe-success", kwargs={
                    "sd_order_id": order.sd_order_id
                }),
                cancel_url=settings.HOST + reverse("stripe-cancel", kwargs={
                    "sd_order_id": order.sd_order_id
                }),
                line_items=items,
                mode="payment",
                payment_intent_data={
                    "capture_method": "manual"
                }
            )
        order.stripe_order_id = session.id
        order.save()

        if multiple_sessions:
            return redirect_error(450, link=session.url)
        return redirect(session.url)


class StripeCheckoutCompleted(View):
    def get(self, request, sd_order_id=None, **kwargs):
        try:
            order = Order.objects.get(sd_order_id=sd_order_id)
        except Order.DoesNotExist:
            return redirect("not-found")
        
        try:
            session = stripe.checkout.Session.retrieve(order.stripe_order_id)
            if not session.payment_intent:
                raise ValueError("No PaymentIntent associated with this checkout session")
            payment_intent = stripe.payment_intent.PaymentIntent.retrieve(session.payment_intent)
        except Exception as e:
            return redirect_error(451)
        
        if not payment_intent.status == "requires_capture":
            return redirect_error(452)

        try:
            capture = payment_intent.capture()
        except Exception as e:
            return redirect_error(453)
        
        order.status = "paid"
        order.save()

        mail.send(
            order.participant.user.email,
            "Snowdays <noreply@snowdays.it>",
            template="payment-confirmation",
            context={
                'host': settings.HOST,
                'participant': order.participant,
                'CODE': order.sd_order_id[27:]
            },
            priority='now'
        )
        return redirect('/success-checkout')


class StripeCheckoutCanceled(View):
    def get(self, request, **kwargs):
        return redirect('/unsuccess-checkout')