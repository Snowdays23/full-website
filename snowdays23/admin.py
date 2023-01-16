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

from django.contrib import admin
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.utils.html import format_html

from snowdays23.models import Participant, University, Sport, MerchItem, EatingHabits, Gear, AllowedParticipant, AllowedAlumnus, InternalUserType, Residence


def register(model, **kw):
    """
    Register a Model into admin by automatically creating his ModelAdmin and
    filling it with values from keyword arguments

    :param model: The Model to be registered
    :param kw: Attributes to be added to the ModelAdmin class
    :return:
    """
    class CustomAdmin(admin.ModelAdmin):
        pass
    for i in kw:
        setattr(CustomAdmin, i, kw[i])
    admin.site.register(model, CustomAdmin)


register(Sport)
register(Gear)
register(MerchItem)
register(EatingHabits)
register(InternalUserType)
register(
    AllowedParticipant,
    search_fields=("email__icontains", )
)
register(
    AllowedAlumnus,
    search_fields=("email__icontains", )
)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "university", "gear", "internal_type")
    search_fields = ("user__last_name__startswith", "user__email__icontains", )

    def gear(self, obj):
        return format_html(
            ", ".join([g.get_name_display() for g in obj.rented_gear.all()])
        )


class UniversityAdmin(admin.ModelAdmin):
    list_display = ("name", "helpers", "hosted", "rentals")

    def helpers(self, obj):
        return Participant.objects.filter(
            university=obj, 
            internal=True, 
            internal_type__name__icontains="helper"
        ).count()

    def hosted(self, obj):
        return InternalUserType.objects.filter(
            Q(participant__isnull=False, internal=True, university=obj) & (
                Q(participant__order__status="paid") | Q(
                    participant__order__created__gt=datetime.datetime.now(
                        tz=datetime.timezone.utc
                    ) - settings.INTERNALS_EXPIRATION_DELTA
                )
            )
        ).aggregate(Sum('guests'))['guests__sum']

    def rentals(self, obj):
        data = ""
        for gi in Gear.name.field.choices:
            data += "%s: %s</br>" % (
                gi[1], 
                Participant.objects.filter(
                    university=obj
                ).aggregate(count=Count('rented_gear', filter=Q(
                    rented_gear__name=gi[0]
                )))['count']
            )
        return format_html(data)


class ResidenceAdmin(admin.ModelAdmin):
    list_display = ("full_address", "hosted")

    def hosted(self, obj):
        return InternalUserType.objects.filter(participant__residence=obj).count()

admin.site.register(Participant, ParticipantAdmin)
admin.site.register(University, UniversityAdmin)
admin.site.register(Residence, ResidenceAdmin)