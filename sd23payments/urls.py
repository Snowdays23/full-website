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

from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from sd23payments import views

urlpatterns = [
    path('order/<str:sd_order_id>/stripe/checkout', views.CreateStripeCheckout.as_view(), name="stripe-checkout"),
    path('order/<str:sd_order_id>/stripe/success', views.StripeCheckoutCompleted.as_view(), name="stripe-success"),
    path('order/<str:sd_order_id>/stripe/cancel', views.StripeCheckoutCanceled.as_view(), name="stripe-cancel")
]