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

import re
import datetime
import secrets
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum

from rest_framework import serializers

from sd23log.models import Event


class NewEventSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False)

    def validate(self, data):
        data["slug"] = slugify(data["name"])
        return data

    class Meta:
        model = Event
        fields = (
            'name',
            'slug',
            'description',
            'icon',
            'only_participants'
        )


class EventSerializer(serializers.ModelSerializer):
    checked_in = serializers.IntegerField()
    left = serializers.IntegerField()
    expected = serializers.IntegerField()

    def get_checked_in(self, event):
        return event.checked_in

    def left(self, event):
        return event.to_be_checked_in

    def expected(self, event):
        return event.expected
    
    class Meta:
        model = Event
        fields = (
            'name',
            'slug',
            'description',
            'icon',
            'only_participants',
            'checked_in',
            'left',
            'expected'
        )