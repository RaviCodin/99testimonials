from django.db import models

# Create your models here.
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserDetails
from payments.serializers import PricingPlanSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password']

    def create(self, validated_data):
        name_parts = validated_data['name'].split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserDetailsSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    first_name = serializers.CharField(
        source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    pricing_plan = PricingPlanSerializer(read_only=True)

    class Meta:
        model = UserDetails
        fields = ['user', 'first_name', 'last_name',
                  'gender', 'country', 'phone', 'display_picture', 'pricing_plan']
        ref_name = 'CustomUserDetailsSerializer'
