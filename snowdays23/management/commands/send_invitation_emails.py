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

from snowdays23.models import AllowedParticipant

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, dry_run=False, *args, **kwargs):
        allowed = AllowedParticipant.objects.all()
        i = 0
        for p in allowed:
            if dry_run:
                print(f"Sending invitation email to {p.email}...")
            else:
                mail.send(
                    p.email,
                    "Snowdays <noreply@snowdays.it>",
                    template="form-invitation",
                    context={
                        'host': settings.HOST
                    },
                    headers={
                        'X-Image-Url': settings.HOST + "/static/logo192.png"
                    }
                )
            i += 1
        print(f"{i} emails sent (or queued depending on default priority)")
        