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

import datetime
import re

from django import forms
from django.conf import settings
from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from post_office import mail

from snowdays23.models import PartyBeast, Policies
from sd23payments.models import Order, BillableItem


class PartyBeastForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        label=_("First name")
    )

    last_name = forms.CharField(
        required=True,
        label=_("Last name")
    )

    email = forms.CharField(
        required=True,
        label=_("Email @unibz.it")
    )

    paid = forms.BooleanField(
        required=False,
        label=_("Paid in person")
    )

    def is_order_to_be_counted(self, o):
        return o.exists() and (o.first().status != "pending" or o.first().created >= datetime.datetime.now(
            tz=o.first().created.tzinfo
        ) - (settings.INTERNALS_EXPIRATION_DELTA if o.participant else settings.PARTY_BEASTS_EXPIRATION_DELTA))

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.lower().endswith("@unibz.it"):
            raise ValidationError(_("Only unibz students can be party beasts. Sorry!"))
        o = Order.objects.filter(
            party_beast__user__email=email,
        )
        if self.is_order_to_be_counted(o):
            raise ValidationError(_("Email is already registered"))
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not re.match(settings.PHONE_NUMBER_REGEX, phone):
            raise ValidationError(_("Phone number is not valid"))
        return phone

    def clean_paid(self):
        return self.cleaned_data.get('paid', False)

    def save(self, commit=True):
        instance = super(PartyBeastForm, self).save(commit=False)
        instance.user = User.objects.update_or_create(
            email__iexact=self.cleaned_data['email'],
            defaults={
                'username': self.cleaned_data['email'],
                'email': self.cleaned_data['email'],
                'first_name': self.cleaned_data['first_name'],
                'last_name': self.cleaned_data['last_name']
            }
        )[0]
        instance.policies = Policies.objects.create(
            privacy=True, 
            terms=True, 
            payment=True
        )

        instance.save()

        ticket = BillableItem.objects.get(slug="party-beast-pack")
        order = Order.objects.create(
            party_beast=instance
        )
        order.items.add(ticket)

        if self.cleaned_data['paid']:
            order.stripe_order_id = "POS"
            order.status = "paid"
            order.save()

            mail.send(
                instance.user.email,
                "Snowdays <noreply@snowdays.it>",
                template="party-payment-confirmation",
                context={
                    "host": settings.HOST,
                    "party_beast": instance,
                    "CODE": order.sd_order_id[27:]
                },
                priority='now'
            )
        else:
            mail.send(
                instance.user.email,
                "Snowdays <noreply@snowdays.it>",
                template="party-form-confirmation",
                context={
                    "host": settings.HOST,
                    "party_beast": instance,
                    'checkout_url': reverse("stripe-checkout", kwargs={
                        "sd_order_id": order.sd_order_id
                    }, current_app="sd23payments")
                },
                priority='now'
            )
        return instance

    class Meta:
        model = PartyBeast
        fields = ('phone', )
    
    field_order = ['first_name', 'last_name', 'email', 'phone', 'paid']