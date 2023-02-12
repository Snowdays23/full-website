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

from django import forms
from django.utils.translation import gettext_lazy as _

from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import render, get_object_or_404, reverse
from django.db.models import Sum, Count, Q
from django.utils.html import format_html
from django.views.generic import View
from django.http import HttpResponse
from django.urls import path

from import_export import resources, fields, widgets
from import_export.admin import ExportMixin

from snowdays23.models import (
    Participant, 
    University, 
    Sport, 
    MerchItem, 
    EatingHabits, 
    Gear, 
    AllowedParticipant, 
    AllowedAlumnus, 
    InternalUserType, 
    Residence,
    PartyBeast
)
from snowdays23 import forms


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

class ExportSportMixin:
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


class ExportCateringMixin:
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


class ExportExternalsMixin:
    def get_queryset(self):
        return Participant.objects.filter(
            internal=False,
            order__isnull=False,
            order__status="paid",
        )


class ExportInternalsMixin:
    def get_queryset(self):
        return Participant.objects.filter(
            internal=True, 
            order__isnull=False, 
            order__status="paid"
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


class ParticipantResourceWithCatering(ExportCateringMixin, ParticipantResource):
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


class ParticipantResourceWithSport(ExportSportMixin, ParticipantResource):
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


class ParticipantResourceWithAllInfo(ExportSportMixin, ExportCateringMixin, ParticipantResource):
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

    def dehydrate_needs_accomodation(self, instance):
        return "YES" if instance.needs_accomodation else "NO"

    def dehydrate_residence(self, instance):
        return instance.residence.full_address if instance.residence else "-"

    def dehydrate_room_nr(self, instance):
        return instance.room_nr if instance.room_nr else "-"

    def dehydrate_internal_type(self, instance):
        return str(instance.internal_type) if instance.internal_type else "-"

    def after_export(self, queryset, data, *args, **kwargs):
        ExportSportMixin.after_export(self, queryset, data, *args, **kwargs)
        ExportCateringMixin.after_export(self, queryset, data, *args, **kwargs)

    class Meta:
        model = Participant
        exclude = (
            'id',
            'user',
            'eating_habits',
            'policies',
            'schlafi',
            'bracelet_id',
            'internal',
        )
        export_order = (
            'first_name',
            'last_name',
            'email',
            'dob',
            'gender',
            'phone',
            'internal_type',
            'university',
            'student_nr',
            'selected_sport',
            'needs_accomodation',
            'vegetarian',
            'vegan',
            'gluten_intolerant',
            'lactose_intolerant',
            'additional_notes',
            'height',
            'weight',
            'shoe_size',
            'helmet_size',
            'rented_gear',
            'residence',
            'room_nr',
        )


class ExternalParticipantResourceWithCatering(ExportExternalsMixin, ParticipantResourceWithCatering):
    pass

class ExternalParticipantResourceWithSport(ExportExternalsMixin, ParticipantResourceWithSport):
    pass

class ExternalParticipantResourceWithAllInfo(ExportExternalsMixin, ParticipantResourceWithAllInfo):
    pass

class InternalParticipantResourceWithCatering(ExportInternalsMixin, ParticipantResourceWithCatering):
    pass

class InternalParticipantResourceWithSport(ExportInternalsMixin, ParticipantResourceWithSport):
    def get_queryset(self):
        return Participant.objects.filter(
            internal=True,
            order__isnull=False,
            order__status="paid",
            rented_gear__isnull=False
        ).distinct()

class InternalParticipantResourceWithAllInfo(ExportInternalsMixin, ParticipantResourceWithAllInfo):
    pass

class ExternalUniversityPhonesResource(resources.ModelResource):
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

    class Meta:
        model = Participant
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone'
        )

class ExternalUniversityPhonesView(View):
    def get(self, request, slug=None, **kwargs):
        university = get_object_or_404(University, slug=slug)
        dataset = ExternalUniversityPhonesResource().export(
            Participant.objects.filter(university=university)
        )
        response = HttpResponse(dataset.csv, content_type="csv")
        response['Content-Disposition'] = f"attachment; filename=phonenrs_{university.slug}.csv"
        return response

class ParticipantAdmin(ExportMixin, admin.ModelAdmin):
    resource_classes = [
        ExternalParticipantResourceWithCatering,
        ExternalParticipantResourceWithSport,
        ExternalParticipantResourceWithAllInfo,
        InternalParticipantResourceWithCatering,
        InternalParticipantResourceWithSport,
        InternalParticipantResourceWithAllInfo,
    ]
    list_display = ("first_name", "last_name", "email", "university", "gear", "internal_type")
    search_fields = ("user__last_name__startswith", "user__email__icontains", )

    def gear(self, obj):
        return format_html(
            ", ".join([g.get_name_display() for g in obj.rented_gear.all()])
        )


class UniversityAdmin(admin.ModelAdmin):
    list_display = ("name", "helpers", "hosted", "full", "rentals", "distinct_types_counter", "party_beasts", "phones")

    def get_urls(self):
        return [
            *super().get_urls(),
            path('phones/<str:slug>', self.admin_site.admin_view(ExternalUniversityPhonesView.as_view()), name='phones')
        ]

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

    def full(self, obj):
        return Participant.objects.filter(
            university=obj,
            internal=True,
            internal_type__name="full",
            order__status="paid"
        ).count()

    def party_beasts(self, obj):
        if not obj.slug == "unibz":
            return 0
        paid = PartyBeast.objects.filter(
            order__status="paid"
        ).count()
        payable = PartyBeast.objects.filter(
            order__status="pending",
            order__created__gt=datetime.datetime.now(
                tz=datetime.timezone.utc
            ) - settings.PARTY_BEASTS_EXPIRATION_DELTA
        ).count()
        return format_html(f"<b>Total</b>: {paid + payable}<br><br><b>Paid</b>: {paid}<br><b>Valid pending</b>: {payable}")

    def distinct_types_counter(self, obj):
        paid_internals = Participant.objects.filter(
            university=obj,
            internal=True,
            order__status="paid"
        )
        if paid_internals.count() == 0:
            return "-"
        paid_externals = Participant.objects.filter(
            internal=False,
            order__status="paid"
        ).count()
        alumni = paid_internals.filter(
            internal_type__name="alumnus"
        ).count()
        host1 = paid_internals.filter(
            internal_type__name="host",
            internal_type__guests=1
        ).count()
        host2 = paid_internals.filter(
            internal_type__name="host",
            internal_type__guests=2
        ).count()
        host3 = paid_internals.filter(
            internal_type__name="host",
            internal_type__guests=3
        ).count()
        host4 = paid_internals.filter(
            internal_type__name="host",
            internal_type__guests=4
        ).count()
        helpers = paid_internals.filter(
            internal_type__name="helper",
        ).count()
        helper_host1 = paid_internals.filter(
            internal_type__name="host+helper",
            internal_type__guests=1
        ).count()
        helper_host2 = paid_internals.filter(
            internal_type__name="host+helper",
            internal_type__guests=2
        ).count()
        helper_host3 = paid_internals.filter(
            internal_type__name="host+helper",
            internal_type__guests=3
        ).count()
        helper_host4 = paid_internals.filter(
            internal_type__name="host+helper",
            internal_type__guests=4
        ).count()

        return format_html(f"<b>Externals:</b> {paid_externals}<br><b>Alumni:</b> {alumni}<br><b>Host 1:</b> {host1}<br><b>Host 2:</b> {host2}<br><b>Host 3:</b> {host3}<br><b>Host 4:</b> {host4}<br><b>Helpers:</b> {helpers}<br><b>Helper + Host 1:</b> {helper_host1}<br><b>Helper + Host 2:</b> {helper_host2}<br><b>Helper + Host 3:</b> {helper_host3}<br><b>Helper + Host 4:</b> {helper_host4}")

    def rentals(self, obj):
        data = ""
        for gi in Gear.name.field.choices:
            data += "%s: %s</br>" % (
                gi[1], 
                Participant.objects.filter(
                    university=obj,
                    order__status="paid"
                ).aggregate(count=Count('rented_gear', filter=Q(
                    rented_gear__name=gi[0]
                )))['count']
            )
        return format_html(data)

    def phones(self, obj):
        return format_html(f'<a href="{reverse("admin:phones", args=(obj.slug, ))}">Download</a>')


class ResidenceAdmin(admin.ModelAdmin):
    list_display = ("full_address", "hosted")

    def hosted(self, obj):
        return Participant.objects.filter(
            residence=obj,
            internal=True
        ).aggregate(Sum('internal_type__guests'))['internal_type__guests__sum']


class PartyBeastAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "paid", "paid_in_person")

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            return super().get_form(request, obj, **kwargs)
        return forms.PartyBeastForm

    def paid(self, obj):
        return obj.order_set.filter(
            items__slug="party-beast-pack",
            status="paid",
        ).exists()

    def paid_in_person(self, obj):
        return obj.order_set.filter(
            items__slug="party-beast-pack",
            status="paid",
            stripe_order_id="POS"
        ).exists()

    paid.boolean = True
    paid_in_person.boolean = True

admin.site.register(Participant, ParticipantAdmin)
admin.site.register(University, UniversityAdmin)
admin.site.register(Residence, ResidenceAdmin)
admin.site.register(PartyBeast, PartyBeastAdmin)