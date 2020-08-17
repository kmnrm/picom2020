from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from django.contrib.auth.models import Group, User
from django.contrib.auth.hashers import make_password


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    group = serializers.SerializerMethodField()

    class Meta(BaseUserRegistrationSerializer.Meta):
        model = User
        fields = ('id', 'username', 'password', 'group',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        users_group = Group.objects.get(name='users')
        user.groups.add(users_group)
        return user

    def get_group(self, user):
        return user.groups.all().first().name
