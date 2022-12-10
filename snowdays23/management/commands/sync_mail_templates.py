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

import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, clean=False, *args, **kwargs):
        for d in os.listdir(settings.POST_OFFICE_TEMPLATES_DIR):
            if os.path.isdir(Path(settings.POST_OFFICE_TEMPLATES_DIR) / d):
                t_dir = settings.POST_OFFICE_TEMPLATES_DIR / d
                t = EmailTemplate.objects.get_or_create(name=d)[0]
                with open(t_dir / f"subject.txt") as fh:
                    t.subject = fh.read().strip()
                if os.path.exists(t_dir / f"content.txt"):
                    with open(t_dir / f"content.txt") as fh:
                        t.content = fh.read().strip()
                if os.path.exists(t_dir / f"content.html"):
                    with open(t_dir / f"content.html") as fh:
                        t.html_content = fh.read().strip()
                t.save()