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

import datetime
import random

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from snowdays23.models import University, EatingHabits, Participant

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true')

    def randomize_age(self):
        return datetime.date.today() - datetime.timedelta(days=365 * random.randrange(18, 30))

    def randomize_eating_habits(self):
        return EatingHabits.objects.create(
            vegetarian=random.choice([True, False]),
            vegan=random.choice([True, False]),
            gluten_free=random.choice([True, False])
        )

    def randomize_bracelet_id(self):
        return "".join(["0123456789abcdef"[random.randrange(len("0123456789abcdef"))] for _ in range(16)])

    def clean_db(self):
        User.objects.all().delete()
        University.objects.all().delete()

    def handle(self, clean=False, *args, **kwargs):
        if clean:
            self.clean_db()
            return
        # Create test user
        u = User.objects.create(
            username="test@snowdays.it",
            email="test@snowdays.it",
            first_name="Test",
            last_name="One"
        )
        # Create test university
        uni = University.objects.create(
            name="Test Uni",
            email_domain="testuni.snowdays.it"
        )
        # Create participant for test user
        p = Participant.objects.create(
            user=u,
            dob=self.randomize_age(),
            bracelet_id=self.randomize_bracelet_id(),
            university=uni,
            eating_habits=self.randomize_eating_habits(),
            internal=False
        )

        print(f"Created participant with uid {p.bracelet_id}")

        u = User.objects.create(
            username="test2@snowdays.it",
            email="test2@snowdays.it",
            first_name="Test",
            last_name="Two"
        )
        uni = University.objects.create(
            name="Host Uni",
            email_domain="hostuni.snowdays.it"
        )
        p1 = Participant.objects.create(
            user=u,
            dob=self.randomize_age(),
            bracelet_id=self.randomize_bracelet_id(),
            university=uni,
            eating_habits=self.randomize_eating_habits(),
            internal=True
        )

        p.schlafi = p1
        p.save()
        p1.save()
