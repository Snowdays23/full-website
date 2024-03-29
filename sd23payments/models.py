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

import secrets

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from snowdays23.models import Participant, PartyBeast

import sd23payments.utils


class BillableItem(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name=_("display name of item")
    )

    slug = models.CharField(
        max_length=16,
        verbose_name=_("id of item")
    )

    price = models.IntegerField(
        verbose_name=_("unit price of item in cents")
    )

    def __str__(self):
        price_eur = self.price / 100.
        return f"{self.name} ({price_eur:.2f} €)"


class Order(models.Model):
    sd_order_id = models.CharField(
        max_length=32,
        verbose_name=_("unique alphanumerical string identifying order internally"),
        default=sd23payments.utils.generate_sd_order_id
    )

    stripe_order_id = models.CharField(
        max_length=92,
        verbose_name=_("stripe order id assigned during checkout"),
        blank=True,
        null=True
    )

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("participant that placed this order")
    )

    party_beast = models.ForeignKey(
        PartyBeast,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("party beast that placed this order")
    )

    status = models.CharField(
        choices=[
            ("pending", _("Not paid")),
            ("paid", _("Paid"))
        ],
        max_length=8,
        default="pending"
    )

    created = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name=_("creation date and time of this order")
    )

    items = models.ManyToManyField(
        BillableItem,
        blank=True,
        verbose_name=_("items included in this order")
    )

    def save(self, *args, **kwargs):
        if not self.participant and not self.party_beast:
            raise ValidationError(
                _("Orders must either be placed by a participant or a party beast"),
                code='order_without_buyer'
            )
        if self.participant and self.party_beast:
            raise ValidationError(
                _("Orders must either be placed by a participant or a party beast"),
                code='order_with_multiple_buyers'
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sd_order_id} [{self.status}] for {self.participant if self.participant else self.party_beast}"