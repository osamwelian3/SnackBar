from dataclasses import fields
from django.contrib.auth.models import User
from rest_framework import serializers
from user_profile.models import UserProfile
from social_auth.models import GoogleSocialUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class SocialAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleSocialUser
        fields = ['id', 'username', 'date_joined']
