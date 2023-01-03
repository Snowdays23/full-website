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

import stripe

stripe.api_key = settings.STRIPE_SECRET_API_KEY


class CreateStripeCheckout(View):
    def get(self, request, sd_order_id=None):
        try:
            order = Order.objects.get(sd_order_id=sd_order_id)
        except Order.DoesNotExist:
            return redirect("not-found")

        if order.status == "paid":
            return redirect("not-found")
        
        if order.stripe_order_id:
            # TODO: alert the user: only the latest payment session will succeed
            print(f"Order already has a stripe checkout session associated to it, continuing...")

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
            # TODO: alert the user: error retrieving checkout session or payment intent, 
            # something went wrong and the user needs to start the payment process over
            print(f"Could not retrieve payment status: {e!r}")
            return redirect("not-found")
        
        print(payment_intent)

        if not payment_intent.status == "requires_capture":
            # TODO: alert the user: payment not ready to be captured, start over
            print(f"PaymentIntent in invalid status to be captured: {payment_intent.status}")
            return redirect("not-found")

        try:
            capture = payment_intent.capture()
            print("captured")
        except Exception as e:
            # TODO: alert the user: payment could not be captured, contact team
            print(f"Could not capture payment: {e!r}")
            return redirect("not-found")
        
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