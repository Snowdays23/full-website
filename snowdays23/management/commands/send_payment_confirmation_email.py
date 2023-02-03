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
from django.core.management.base import BaseCommand, CommandError

from post_office import mail

from sd23payments.models import Order

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('sd_order_id', type=str)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, sd_order_id=None, dry_run=False, *args, **kwargs):
        if not sd_order_id:
            sys.exit(f"Usage: {sys.argv[0]} [--dry-run] <sd_order_id>")
        try:
            order = Order.objects.get(sd_order_id=sd_order_id)
        except:
            sys.exit(f"Order {sd_order_id} not found")
        if order.status != "paid":
            sys.exit(f"Order {sd_order_id} has status {order.status}. Not sending payment confirmation.")
        print(f"Sending payment confirmation to {order.participant.email}...")
        if not dry_run:
            mail.send(
                order.participant.email,
                "Snowdays <noreply@snowdays.it>",
                template="payment-confirmation",
                context={
                    "host": settings.HOST,
                    "participant": order.participant,
                    "CODE": order.sd_order_id[27:]
                }
            )