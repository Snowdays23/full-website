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

import base64
import requests
import json


PAYPAL_API_URL = "https://api-m.sandbox.paypal.com/"


@staticmethod
def create_order(amount):
    token = generate_access_token()
    if not token:
        raise Exception('Could not generate access token')
    r = requests.post(PAYPAL_API_URL + f"v2/checkout/orders", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }, data=json.dumps({
        "intent": "CAPTURE",
        "purchase_units": {
            "amount": {
                "currency_code": "EUR",
                "value": "%.2f" % amount
            }
        }
    }))
    return r.json() if r.ok else None


@staticmethod
def capture_payment(order_id):
    token = generate_access_token()
    if not token:
        raise Exception('Could not generate access token')
    r = requests.post(PAYPAL_API_URL + f"v2/checkout/orders/{order_id}/capture", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    })
    return r.json() if r.ok else None


@staticmethod
def generate_access_token():
    auth = base64.b64encode(f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_SECRET}")
    r = requests.post(PAYPAL_API_URL + "v1/oauth2/token", data={
        "grant_type": "client_credentials"
    }, headers={
        "Authorization": f"Basic {auth}"
    })

    if not r.ok:
        return None

    return r.json()['access_token']