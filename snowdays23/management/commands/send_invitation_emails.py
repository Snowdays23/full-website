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
from post_office.models import Email

from snowdays23.models import AllowedParticipant

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--resend', action='store_true')

    def handle(self, dry_run=False, resend=False, *args, **kwargs):
        allowed = AllowedParticipant.objects.all()
        i = 0
        for p in allowed:
            sent = Email.objects.filter(
                to__iexact=p.email,
                template__name="form-invitation",
                status=0
            ).exists()
            if dry_run:
                if sent:
                    if resend:
                        print(f"Invitation already sent to {p.email}, but resend specified: resending...")
                    else:
                        print(f"Invitation already sent to {p.email}, skipping...")
                else:
                    print(f"Sending invitation email to {p.email}...")
            else:
                if not sent or resend:
                    mail.send(
                        p.email,
                        "Snowdays <noreply@snowdays.it>",
                        template="form-invitation",
                        context={
                            'host': settings.HOST
                        }
                    )
                else:
                    print(f"Invitation already sent to {p.email} and no resend specified, skipping...")
            i += 1 if not sent or resend else 0
        print(f"{i} emails sent (or queued depending on default priority)")
        