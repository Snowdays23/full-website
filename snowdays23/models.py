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

from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class University(models.Model):
    slug = models.CharField(
        max_length=8,
        verbose_name=_("code identifying university")
    )

    name = models.TextField(
        verbose_name=_("full name of institution")
    )

    email_domain = models.TextField(
        verbose_name=_("domain name associated with this university"),
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} <{self.email_domain}>"

    class Meta:
        verbose_name_plural = _("Universities")


class Gear(models.Model):
    name = models.CharField(
        choices=[
            ("ski", _("Skii")),
            ("snowboard", _("Snowboard")),
            ("helmet", _("Helmet")),
            ("poles", _("Skii Poles")),
            ("skiboots", _("Skii Boots")),
            ("snowboardboots", _("Snowboard Boots"))
        ],
        max_length=16,
        default="ski",
        verbose_name=_("name of rented gear"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _("Gear items")


class EatingHabits(models.Model):
    vegetarian = models.BooleanField(
        default=False,
        verbose_name=_("vegetarian")
    )

    vegan = models.BooleanField(
        default=False,
        verbose_name=_("vegan")
    )

    gluten_free = models.BooleanField(
        default=False,
        verbose_name=_("gluten intolerant")
    )

    lactose_free = models.BooleanField(
        default=False,
        verbose_name=_("lactose intolerant")
    )

    class Meta:
        verbose_name_plural = _("Eating habits objects")


class Sport(models.Model):
    name = models.TextField(
        verbose_name=_("name of this sport activity")
    )

    rules = models.TextField(
        verbose_name=_("rules and details of this sport activity"),
        null=True,
        blank=True
    )

    start = models.DateTimeField(
        verbose_name=_("starting time of this scheduled sport activity"),
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{name} at {start!r}"


class MerchItem(models.Model):
    name = models.TextField(
        verbose_name=_("name identifying this item")
    )

    size = models.CharField(
        choices=[
            ("NA", _("not applicable")),
            ("U", _("unisize")),
            ("S", _("small")),
            ("M", _("medium")),
            ("L", _("large")),
            ("XL", _("extra large"))
        ],
        max_length=2,
        default="NA",
        verbose_name=_("size of this item (if applicable)"),
    )

    color = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("color code of this item (if applicable)")
    )

    def __str__(self):
        return f"{self.name} (size {self.size}, color {self.color})"


class Policies(models.Model):
    privacy = models.BooleanField(
        default=False,
        verbose_name=_("has read and accepted privacy policy")
    )

    terms = models.BooleanField(
        default=False,
        verbose_name=_("has read and accepted terms and conditions")
    )

    payment = models.BooleanField(
        default=False,
        verbose_name=_("has read and accepted payment policy")
    )


class Participant(models.Model):
    user = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        verbose_name=_("system user associated with this participant")
    )

    dob = models.DateField(
        verbose_name=_("date of birth")
    )

    gender = models.CharField(
        choices=[
            ("M", _("male")),
            ("F", _("female")),
            ("N", _("other/neutral/unspecified"))
        ],
        max_length=1,
        verbose_name=_("gender"),
        default="N"
    )

    phone = models.CharField(
        max_length=16,
        verbose_name=_("personal mobile number")
    )

    student_nr = models.CharField(
        max_length=16,
        verbose_name=_("registration number within university")
    )

    bracelet_id = models.CharField(
        max_length=16,
        verbose_name=_("UID of the RFID bracelet associated with this participant"),
        null=True,
        blank=True
    )

    height = models.IntegerField(
        verbose_name=_("height in centimeters"),
        null=True,
        blank=True
    )

    weight = models.IntegerField(
        verbose_name=_("weight in kilograms"),
        null=True,
        blank=True
    )

    shoe_size = models.IntegerField(
        verbose_name=_("european shoe size"),
        null=True,
        blank=True
    )

    helmet_size = models.CharField(
        choices=[
            ("XS", _("extra small")),
            ("S", _("small")),
            ("M", _("medium")),
            ("L", _("large")),
            ("XL", _("extra large"))
        ],
        max_length=2,
        verbose_name=_("head size"),
        null=True,
        blank=True
    )

    university = models.ForeignKey(
        University,
        on_delete=models.PROTECT,
        verbose_name=_("university to which this participant is enrolled")
    )

    eating_habits = models.ForeignKey(
        EatingHabits,
        on_delete=models.CASCADE,
        verbose_name=_("special eating needs declared by this participant")
    )

    additional_notes = models.TextField(
        verbose_name=_("additional requests specified by this participant"),
        blank=True,
        null=True
    )

    internal = models.BooleanField(
        default=False,
        verbose_name=_("flag indicating whether this participant belongs to the host university")
    )

    needs_accomodation = models.BooleanField(
        default=False,
        verbose_name=_("flag indicating whether this participant needs a schlafi")
    )

    schlafi = models.ForeignKey(
        "snowdays23.Participant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("internal participant hosting this participant")
    )

    selected_sport = models.CharField(
        choices=[
            ("ski", _("Skii")),
            ("snowboard", _("Snowboard")),
            ("none", _("None"))
        ],
        max_length=16,
        verbose_name=_("selected sport during sign-up"),
        default="none"
    )

    rented_gear = models.ManyToManyField(
        Gear,
        blank=True,
        verbose_name=_("equipment items requested for rental")
    )

    policies = models.ForeignKey(
        Policies,
        on_delete=models.PROTECT,
        verbose_name=_("status of sign-up policies"),
        null=True,
        blank=True
    )

    def __str__(self):
        return f"#{self.pk} [{self.bracelet_id}] {self.first_name} {self.last_name} <{self.email}> ({self.university.name})"

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    @property
    def username(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.schlafi and self.internal:
            raise ValidationError(
                _("Schlafi guest must be an external participant"),
                code='schlafi_guest_must_be_external'
            )
        if self.schlafi and not self.schlafi.internal:
            raise ValidationError(
                _("Schlafi host must be an internal participant"),
                code='schlafi_host_must_be_internal'
            )
        super().save(*args, **kwargs)

    def delete(self, **kwargs):
        self.rented_gear.clear()
        super().delete(**kwargs)

    class Meta:
        unique_together = ('university', 'student_nr')


class AllowedParticipant(models.Model):
    email = models.TextField(
        verbose_name=_("pre-registered email provided by guest uni")
    )

    def __str__(self):
        return self.email