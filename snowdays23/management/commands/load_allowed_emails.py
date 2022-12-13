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
import csv
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from snowdays23.models import AllowedParticipant

EMAIL_REG = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csvpath', type=str)
        parser.add_argument('--clean', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, csvpath=None, clean=False, verbose=False, *args, **kwargs):
        if not csvpath:
            sys.exit(f"Usage: {sys.argv[0]} [--clean] <csv path>")
        if clean:
            AllowedParticipant.objects.all().delete()
            print("Deleted all allowed participants")
        with open(csvpath, "r") as csvf:
            r = csv.reader(csvf)
            for row in r:
                if len(row) < 4 or not row[1] or not row[2]:
                    if verbose:
                        print("Invalid row, skipping...")
                    continue
                if not re.fullmatch(EMAIL_REG, row[3]):
                    if verbose:
                        print(f"[W] Invalid email detected: {row[2]}, proceeding anyway...")
                
                print(f"Adding {row[1]} {row[2]} ({row[3]}) to the allowed participants")
                AllowedParticipant.objects.create(email=row[3])