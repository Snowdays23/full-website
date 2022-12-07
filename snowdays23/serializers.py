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

import re

from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers

from snowdays23.models import Participant, EatingHabits, University


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class EatingHabitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EatingHabits
        fields = '__all__'


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
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


class NewParticipantSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    eating_habits = EatingHabitsSerializer()
    university = serializers.CharField()

    def validate_university(self, slug):
        if not slug:
            raise serializers.ValidationError("university code cannot be null")
        try:
            university = University.objects.get(slug=slug)
        except University.DoesNotExist:
            raise serializers.ValidationError("university code is not valid")
        return slug
    
    def validate_email(self, email):
        # FIXME: validate email against known list
        return email

    def validate_phone(self, phone):
        if not re.match(settings.PHONE_NUMBER_REGEX, phone):
            raise serializers.ValidationError("phone number is not valid")
        return phone

    def validate(self, data):
        university_code = data.get('university')
        student_nr = data.get('student_nr')
        if Participant.objects.filter(university__slug=data, student_nr=student_nr).exists():
            raise serializers.ValidationError('duplicate student number within the same university')
        return data

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        university = University.objects.get(slug=validated_data.pop('university'))
        eating_habits = EatingHabits.objects.create(**validated_data.pop('eating_habits'))
        participant = Participant.objects.create(
            user=User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email
            ),
            university=university,
            eating_habits=eating_habits,
            **validated_data
        )
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
            'height',
            'weight',
            'shoe_size',
            'helmet_size'
        )