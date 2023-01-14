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

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from snowdays23.models import Participant
from sd23payments.models import Order


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, dry_run=False, *args, **kwargs):
        expired = Order.objects.filter(
            participant__internal=True,
            created__lt=datetime.datetime.now() - settings.INTERNALS_EXPIRATION_DELTA,
            status="pending"
        )

        for e in expired:
            print(f"Deleting {e.participant!r} created on {e.created}...")
            if not dry_run:
                e.participant.user.delete()

        if dry_run:
            print("Dry run complete. No participants deleted, re-run without --dry-run to apply.")