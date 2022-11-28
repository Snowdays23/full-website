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

from rest_framework.views import APIView

from sd23payments.models import Order
from sd23payments.utils import create_order, capture_payment


class PlaceOrder(APIView):
    def post(self, request, sd_order_id=None):
        try:
            order = Order.objects.get(order_id=sd_order_id)
        except Order.NotFound:
            return JsonResponse({
                # TODO: handle error
            })

        amount = order.amount
        pp_order = create_order(amount)
        if not pp_order:
            pass # TODO: handle error
        return JsonResponse(pp_order)


class CaptureOrder(APIView):
    def post(self, request, pp_order_id=None):
        pass