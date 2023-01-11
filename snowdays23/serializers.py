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

from snowdays23.models import Participant, AllowedParticipant, EatingHabits, University, Gear, Policies, Residence, InternalUserType
from sd23payments.models import Order


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


class ResidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Residence
        fields = [
            'address',
            'street_nr',
            'city',
            'postal_code',
            'is_college',
            'college_slug'
        ]
    
    def validate(self, data):
        if data['city'].lower() not in [
            "bolzano", 
            "bozen", 
            "bolzano bozen", 
            "bolzano/bozen", 
            "bolzano-bozen"
        ] or data['postal_code'] != "39100":
            raise serializers.ValidationError(_("Host participants must be located in Bolzano/Bozen"))
        if data['is_college']:
            try:
                college = Residence.objects.get(college_slug=data['college_slug'])
            except Residence.DoesNotExist:
                raise serializers.ValidationError(_("Invalid college"))
            data['address'] = college.address
            data['street_nr'] = college.street_nr
            data['postal_code'] = college.postal_code
            data['city'] = college.city
            data['college_name'] = college.college_name
            data['max_guests'] = college.max_guests
        return data


class NewParticipantSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    eating_habits = EatingHabitsSerializer()
    university = serializers.CharField()
    needs_rent = serializers.BooleanField(write_only=True)
    residence = ResidenceSerializer(required=False)
    rented_gear = GearSerializer(many=True)
    policies = PoliciesSerializer()
    is_helper = serializers.BooleanField(required=False)
    is_host = serializers.BooleanField(required=False)
    guests = serializers.IntegerField(required=False)

    def validate_university(self, slug):
        if not slug:
            raise serializers.ValidationError(_("University code is not valid"))
        try:
            university = University.objects.get(slug=slug)
        except University.DoesNotExist:
            raise serializers.ValidationError(_("University code is not valid"))
        return slug
    
    def validate_email(self, email):
        unibz = email.lower().endswith("@unibz.it")
        if settings.STRICT_ALLOWED_EMAIL_CHECK and not unibz:
            if not AllowedParticipant.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError(_("Email is not an allowed participant"))

        if unibz:
            o = Order.objects.filter(participant__user__email__iexact=email)
            if o.exists() and o.first().status != "pending":
                raise serializers.ValidationError(_("Email is already registered"))
        elif User.objects.filter(email__iexact=email).exists():
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

        email = data.get('email')
        if university_code == "unibz":
            if not email.endswith("@unibz.it"):
                raise serializers.ValidationError(_("Internal participants must register with unibz email address"))
            data['internal'] = True
        else:
            data['internal'] = False 

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

        if data['internal']:
            user_types = []
            is_host = data['is_host']
            is_helper = data['is_helper']
            can_enrol_helpers = InternalUserType.can_enrol_type("helper")
            can_enrol_hosts = InternalUserType.can_enrol_type("host")
            if is_host:
                if not can_enrol_hosts:
                    raise serializers.ValidationError(_("No host slots left"))
                user_types.append("host")
            if is_helper:
                if not can_enrol_helpers:
                    raise serializers.ValidationError(_("No helper slots left"))
                user_types.append("helper")
            if not is_host and not is_helper and (can_enrol_hosts or can_enrol_helpers):
                raise serializers.ValidationError(_("Only enrolling helpers and hosts"))
            
            user_type = "+".join(user_types) if len(user_types) > 0 else "full"
            
            guests = data.pop('guests', 0)
            if data['residence']['is_college']:
                college = Residence.objects.get(college_slug=data['residence']['college_slug'])
                if guests > college.max_guests:
                    raise serializers.ValidationError(_("Too many guests for the specified residence: check the rules!"))
            else:
                # maximum number of guests for any residence must not be selectable by the user:
                # drop it if present in the request
                if "max_guests" in data['residence']:
                    del data['residence']['max_guests']
            data['internal_user_type'] = {
                "name": user_type,
                "guests": guests
            }
        else:
            # Remove (reset) fields allowed on internal participants only
            data['is_helper'] = False
            data['is_host'] = False
            data['residence'] = None
            data['room_nr'] = None
            if "guests" in data:
                del data['guests']

        return data

    def create(self, validated_data):
        email = validated_data.pop('email')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        university = University.objects.get(slug=validated_data.pop('university'))
        eating_habits = EatingHabits.objects.create(**validated_data.pop('eating_habits'))
        rented_gear = validated_data.pop('rented_gear')
        needs_rent = validated_data.pop('needs_rent')
        policies = Policies.objects.create(**validated_data.pop('policies'))
        is_helper = validated_data.pop('is_helper', False)
        is_host = validated_data.pop('is_host', False)
        residence = validated_data.pop('residence', None)
        if not is_host:
            residence = None
        elif residence['is_college']:
            residence = Residence.objects.get(college_slug=residence['college_slug'])
        else:
            residence = Residence.objects.create(**residence)
        if "internal_user_type" in validated_data:
            internal_user_type = InternalUserType.objects.create(**validated_data.pop('internal_user_type'))
        else:
            internal_user_type = None
        
        participant, created = Participant.objects.update_or_create(
            user__email__iexact=email,
            defaults={
                'user': User.objects.update_or_create(
                    email__iexact=email, 
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'username': email
                    }
                )[0],
                'university': university,
                'eating_habits': eating_habits,
                'policies': policies,
                'internal_type': internal_user_type,
                'residence': residence,
                **validated_data
            }
        )
        # participant = Participant.objects.create(
        #     user=User.objects.create(
        #         first_name=first_name,
        #         last_name=last_name,
        #         email=email,
        #         username=email
        #     ),
        #     university=university,
        #     eating_habits=eating_habits,
        #     policies=policies,
        #     internal_type=internal_user_type,
        #     residence=residence,
        #     **validated_data
        # )
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
            'residence',
            'room_nr',
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
            'policies',
            'is_helper',
            'is_host',
            'guests'
        )