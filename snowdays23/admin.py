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
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.utils.html import format_html

from import_export import resources, fields, widgets
from import_export.admin import ExportMixin

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

class ParticipantResource(resources.ModelResource):
    first_name = fields.Field(
        column_name="first_name",
        attribute="user",
        widget=widgets.ForeignKeyWidget(User, "first_name")
    )

    last_name = fields.Field(
        column_name="last_name",
        attribute="user",
        widget=widgets.ForeignKeyWidget(User, "last_name")
    )

    email = fields.Field(
        column_name="email",
        attribute="user",
        widget=widgets.ForeignKeyWidget(User, "email")
    )

    def dehydrate_university(self, instance):
        return instance.university.name

    def dehydrate_dob(self, instance):
        return instance.dob.strftime("%d/%m/%y")

    def export(self, queryset=None, *args, **kwargs):
        return super().export(None, *args, **kwargs)

    def get_queryset(self):
        return Participant.objects.filter(internal=False)


class ParticipantResourceWithCatering(ParticipantResource):
    vegan = fields.Field(
        column_name="vegan"
    )

    vegetarian = fields.Field(
        column_name="vegetarian"
    )

    lactose_intolerant = fields.Field(
        column_name="lactose_intolerant"
    )

    gluten_intolerant = fields.Field(
        column_name="gluten_intolerant"
    )

    def dehydrate_vegan(self, instance):
        return "YES" if instance.eating_habits.vegan else "NO"

    def dehydrate_vegetarian(self, instance):
        return "YES" if instance.eating_habits.vegetarian else "NO"

    def dehydrate_lactose_intolerant(self, instance):
        return "YES" if instance.eating_habits.lactose_free else "NO"

    def dehydrate_gluten_intolerant(self, instance):
        return "YES" if instance.eating_habits.gluten_free else "NO"

    def after_export(self, queryset, data, *args, **kwargs):
        data.append(["" for _ in range(len(self.Meta.export_order))])
        
        row = ["TOTALI"] + ["" for _ in range(len(self.Meta.export_order) - 1)]
        row[self.Meta.export_order.index('vegan')] = str(
            queryset.filter(eating_habits__vegan=True).count()
        )
        row[self.Meta.export_order.index('vegetarian')] = str(
            queryset.filter(eating_habits__vegetarian=True).count()
        )
        row[self.Meta.export_order.index('gluten_intolerant')] = str(
            queryset.filter(eating_habits__gluten_free=True).count()
        )
        row[self.Meta.export_order.index('lactose_intolerant')] = str(
            queryset.filter(eating_habits__lactose_free=True).count()
        )
        data.append(row)

    class Meta:
        model = Participant
        exclude = (
            'id',
            'user',
            'internal',
            'internal_type',
            'eating_habits',
            'policies',
            'residence',
            'room_nr',
            'schlafi',
            'bracelet_id',
            'height',
            'weight',
            'shoe_size',
            'helmet_size',
            'rented_gear',
            'needs_accomodation',
            'selected_sport'
        )
        export_order = (
            'first_name',
            'last_name',
            'email',
            'dob',
            'gender',
            'phone',
            'university',
            'student_nr',
            'vegetarian',
            'vegan',
            'gluten_intolerant',
            'lactose_intolerant',
            'additional_notes'
        )


class ParticipantResourceWithSport(ParticipantResource):
    def dehydrate_rented_gear(self, instance):
        return ", ".join(sorted([g.get_name_display() for g in instance.rented_gear.all()]))

    def after_export(self, queryset, data, *args, **kwargs):
        data.append(["" for _ in range(len(self.Meta.export_order))])
        data.append(["TOTALI"] + ["" for _ in range(self.Meta.export_order.index('rented_gear') - 1)] + [
            "Totals: " + ", ".join([g[1] + ": " + str(queryset.aggregate(
                count=Count('rented_gear', 
                    filter=Q(
                        rented_gear__name=g[0]
                    )
                )
            )['count']) for g in Gear.name.field.choices])
        ] + ["" for _ in range(len(self.Meta.export_order) - 1 - self.Meta.export_order.index('rented_gear'))])

    class Meta:
        model = Participant
        exclude = (
            'id',
            'user',
            'internal',
            'internal_type',
            'eating_habits',
            'policies',
            'residence',
            'room_nr',
            'schlafi',
            'bracelet_id',
            'needs_accomodation',
            'additional_notes'
        )
        export_order = (
            'first_name',
            'last_name',
            'email',
            'dob',
            'gender',
            'phone',
            'university',
            'student_nr',
            'selected_sport',
            'height',
            'weight',
            'shoe_size',
            'helmet_size',
            'rented_gear'
        )


class ParticipantResourceWithPersonalInfo(ParticipantResource):
    
    class Meta:
        model = Participant
        exclude = (
            'id',
            'user',
            'internal',
            'internal_type',
            'eating_habits',
            'policies',
            'residence',
            'room_nr',
            'schlafi',
            'bracelet_id',
            'height',
            'weight',
            'shoe_size',
            'helmet_size',
            'additional_notes',
            'rented_gear'
        )
        export_order = (
            'first_name',
            'last_name',
            'email',
            'dob',
            'gender',
            'phone',
            'university',
            'student_nr',
            'selected_sport',
            'needs_accomodation'
        )


class ParticipantAdmin(ExportMixin, admin.ModelAdmin):
    resource_classes = [ParticipantResourceWithCatering, ParticipantResourceWithSport, ParticipantResourceWithPersonalInfo]
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
            Q(participant__isnull=False, participant__internal=True, participant__university=obj) & (
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
        return Participant.objects.filter(
            residence=obj,
            internal=True
        ).aggregate(Sum('internal_type__guests'))['internal_type__guests__sum']

admin.site.register(Participant, ParticipantAdmin)
admin.site.register(University, UniversityAdmin)
admin.site.register(Residence, ResidenceAdmin)