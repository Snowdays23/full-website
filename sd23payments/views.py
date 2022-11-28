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
from django.shortcuts import render
from django.http import JsonResponse

from rest_framework import status
from rest_framework.views import APIView

from sd23payments.models import Order
from sd23payments.utils import create_order, capture_payment


class PlaceOrder(APIView):
    def post(self, request, sd_order_id=None):
        try:
            order = Order.objects.get(sd_order_id=sd_order_id)
        except Order.DoesNotExist:
            return JsonResponse({
                "name": "RESOURCE_NOT_FOUND",
                "message": "The requested order could not be found.",
                "details": [
                    {
                        "field": "sd_order_id",
                        "value": sd_order_id,
                        "issue": "INVALID_RESOURCE_ID",
                        "description": "The given internal order id is null or does not correspond to any valid order."
                    }
                ]
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
        amount = order.amount
        pp_order = create_order(amount)
        if not pp_order:
            return JsonResponse({
                "name": "INTERNAL_SERVER_ERROR",
                "message": "The server could not process this request at this time."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        order.pp_order_id = pp_order["id"]
        order.save()

        return JsonResponse(pp_order)


class CaptureOrder(APIView):
    def post(self, request, pp_order_id=None):
        capture = capture_payment(pp_order_id)
        if not capture:
            return JsonResponse({
                "name": "INTERNAL_SERVER_ERROR",
                "message": "The server could not process this request at this time."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            order = Order.objects.get(pp_order_id=pp_order_id)
        except Order.DoesNotExist:
            # payment completed but order not found, this should not happen
            return JsonResponse({
                "name": "INTERNAL_SERVER_ERROR",
                "message": "The server could not process this request at this time.",
                "details": [
                    {
                        "field": "pp_order_id",
                        "value": pp_order_id,
                        "issue": "INVALID_RESOURCE_ID",
                        "description": "The PayPal order could not be traced back to the order placed on the shop. Please contact support."
                    }
                ]
            })
        if capture['status'] == "COMPLETED":
            order.status = "paid"
            order.pp_capture = capture
            order.save()

        return JsonResponse(capture)