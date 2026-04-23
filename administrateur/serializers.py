from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from accounts.models import User  # adjust if your app name differs


class UserListSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'telephone',
            'is_approved', 'is_verified', 'is_online',
            'last_login_time', 'date_joined', 'is_active',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login_time', 'is_online']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'role', 'telephone',
            'is_approved', 'is_verified', 'is_active',
        ]

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name',
            'password', 'role', 'telephone',
            'is_approved', 'is_verified', 'is_active',
        ]

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            validated_data['password'] = make_password(password)
        return super().update(instance, validated_data)


class UserApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_approved']