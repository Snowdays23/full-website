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

from django.contrib import admin
from django.utils.html import format_html

from snowdays23.models import Participant, University, Sport, MerchItem, EatingHabits, Gear, AllowedParticipant


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


register(University)
register(Sport)
register(Gear)
register(MerchItem)
register(EatingHabits)
register(
    AllowedParticipant,
    search_fields=("email__icontains", )
)


class ParticipantAdmin(admin.ModelAdmin):
    list_display=("first_name", "last_name", "email", "university", "gear")
    search_fields = ("user__last_name__startswith", "user__email__icontains", )

    def gear(self, obj):
        return format_html(
            ", ".join([g.get_name_display() for g in obj.rented_gear.all()])
        )

admin.site.register(Participant, ParticipantAdmin)