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

import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from post_office import mail
from post_office.models import Email

from snowdays23.models import Participant

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('participants', type=str, nargs=2)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, participants=[], dry_run=False, *args, **kwargs):
        if not participants:
            sys.exit(f"Usage: {sys.argv[0]} <old_participant_email> <new_participant_email>")
        old_participant, new_participant = participants
        try:
            old_participant = Participant.objects.get(user__email__iexact=old_participant)
        except Participant.DoesNotExist:
            sys.exit(f"Error: no participant found with email {old_participant}")
        try:
            new_participant = Participant.objects.get(user__email__iexact=new_participant)
        except Participant.DoesNotExist:
            sys.exit(f"Error: no participant found with email {new_participant}")
        
        old_participant_order = old_participant.order_set.get(items__name__icontains="ticket")
        if old_participant_order.status != "paid":
            sys.exit(f"Error: old order has wrong status: {old_participant_order.status}")
        
        new_participant_order = new_participant.order_set.get(items__name__icontains="ticket")
        if new_participant_order.status == "paid":
            sys.exit(f"Error: new order has already been paid!")
        
        old_email = old_participant.user.email
        if not dry_run:
            new_participant_order.delete()
            old_participant_order.participant = new_participant
            old_participant_order.save()
            old_participant.delete()

        print(f"Deleted old participant ({old_email}), new participant ({new_participant.user.email}) is now bound to order {old_participant_order.sd_order_id}")