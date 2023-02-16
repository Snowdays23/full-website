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
from django.db import models
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from snowdays23.models import Participant, PartyBeast


class CheckIn(models.Model):
    event = models.ForeignKey(
        "sd23log.Event",
        on_delete=models.CASCADE,
        verbose_name=_("event to which check-in is performed")
    )
    
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("checked in participant")
    )

    party_beast = models.ForeignKey(
        PartyBeast,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("checked in party beast")
    )

    scanning_time = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name=_("time of check-in")
    )

    def save(self, *args, **kwargs):
        if self.participant and self.party_beast:
            raise ValidationError(_("check-in can be performed by either a participant or a party beast"))
        if not self.participant and not self.party_beast:
            raise ValidationError(_("check-in must be performed by either a participant or a party beast"))
        super().save(*args, **kwargs)



class Event(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name=_("name of the tracked event")
    )

    slug = models.CharField(
        max_length=64,
        verbose_name=_("short name of the tracked event")
    )

    description = models.TextField(
        verbose_name=_("additional info about this event")
    )

    icon = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        verbose_name=_("id of the icon resource for this event")
    )

    only_participants = models.BooleanField(
        default=True,
        verbose_name=_("flag indicating whether only participants are allowed to be checked in to this event")
    )

    @property
    def checked_in(self):
        return self.checkin_set.count()

    @property
    def left(self):
        if self.only_participants:
            return Participant.objects.count() - self.checkin_set.count()
        return Participant.objects.count() + PartyBeast.objects.count() - self.checkin_set.count()

    @property
    def expected(self):
        if self.only_participants:
            return Participant.objects.count()
        return Participant.objects.count() + PartyBeast.objects.count()