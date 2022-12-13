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
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from snowdays23.models import Participant, AllowedParticipant, EatingHabits, University, Gear, Policies


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class EatingHabitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EatingHabits
        fields = '__all__'

    def validate(self, data):
        if data['vegan']:
            data['vegetarian'] = True
        return data


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'


class GearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gear
        fields = '__all__'


class ParticipantSerializer(serializers.ModelSerializer):
    eating_habits = EatingHabitsSerializer()
    university = UniversitySerializer()
    # schlafi = ParticipantSerializer()

    class Meta:
        model = Participant
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'gender',
            'university',
            'student_nr',
            'dob',
            'phone',
            'eating_habits',
            'additional_notes',
            'bracelet_id',
            'internal',
            'needs_accomodation',
            'schlafi'
        )


class PoliciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Policies
        fields = '__all__'

    def validate(self, data):
        if not data["privacy"] or not data["terms"] or not data["payment"]:
            raise serializers.ValidationError(_("Privacy policy, general terms and payment policy have to be read and accepted to proceed"))
        return data


class NewParticipantSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    eating_habits = EatingHabitsSerializer()
    university = serializers.CharField()
    needs_rent = serializers.BooleanField(write_only=True)
    rented_gear = GearSerializer(many=True)
    policies = PoliciesSerializer()

    def validate_university(self, slug):
        if not slug:
            raise serializers.ValidationError(_("University code is not valid"))
        try:
            university = University.objects.get(slug=slug)
        except University.DoesNotExist:
            raise serializers.ValidationError(_("University code is not valid"))
        return slug
    
    def validate_email(self, email):
        if settings.STRICT_ALLOWED_EMAIL_CHECK:
            if not AllowedParticipant.objects.filter(email=email).exists():
                raise serializers.ValidationError(_("Email is not an allowed participant"))

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(_("Email is already registered"))
        return email

    def validate_phone(self, phone):
        if not re.match(settings.PHONE_NUMBER_REGEX, phone):
            raise serializers.ValidationError(_("Phone number is not valid"))
        return phone

    def validate_dob(self, dob):
        if dob >= datetime.date.today() - relativedelta(years=18):
            raise serializers.ValidationError(_("Participants must be at least 18 years old"))
        return dob

    def validate(self, data):
        university_code = data.get('university')
        student_nr = data.get('student_nr')
        if Participant.objects.filter(university__slug=university_code, student_nr=student_nr).exists():
            raise serializers.ValidationError(_("Duplicate student number within the same university"))
        
        rented_gear = data['rented_gear']
        for i, gear in enumerate(rented_gear):
            if rented_gear.index(gear) != i:
                raise serializers.ValidationError(_("Only one item per type can be selected for rental"))
        if not data['needs_rent'] or not data['selected_sport'] or data['selected_sport'] == "none":
            data['rented_gear'] = []
            data['height'] = None
            data['weight'] = None
            data['helmet_size'] = None
            data['shoe_size'] = None

        return data

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        university = University.objects.get(slug=validated_data.pop('university'))
        eating_habits = EatingHabits.objects.create(**validated_data.pop('eating_habits'))
        rented_gear = validated_data.pop('rented_gear')
        needs_rent = validated_data.pop('needs_rent')
        policies = Policies.objects.create(**validated_data.pop('policies'))
        participant = Participant.objects.create(
            user=User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email
            ),
            university=university,
            eating_habits=eating_habits,
            policies=policies,
            **validated_data
        )
        gear_items = Gear.objects.bulk_create([
            Gear(**gear) for gear in rented_gear
        ])
        participant.rented_gear.set(gear_items)
        participant.save()
        return participant

    class Meta:
        model = Participant
        fields = (
            'first_name',
            'last_name',
            'email',
            'gender',
            'university',
            'student_nr',
            'dob',
            'phone',
            'eating_habits',
            'additional_notes',
            'needs_accomodation',
            'needs_rent',
            'height',
            'weight',
            'shoe_size',
            'helmet_size',
            'rented_gear',
            'selected_sport',
            'policies'
        )