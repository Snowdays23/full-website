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

from django.test import TestCase, Client

class ParticipantTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_internal_creation(self):
        pass

    def test_music_school_creation(self):
        pass

    def test_allowed_alumnus_creation(self):
        pass

    def test_disallowed_alumnus_creation(self):
        pass

    def test_allowed_external_creation(self):
        pass

    def test_disallowed_external_creation(self):
        pass

    def test_sold_out_helper(self):
        pass

    def test_sold_out_host(self):
        pass

    def test_disallowed_full(self):
        pass