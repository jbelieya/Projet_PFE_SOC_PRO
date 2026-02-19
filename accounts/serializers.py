import re

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'telephone']
    def validate_password(self, value):
        if len(value) < 9:
            raise serializers.ValidationError("Password min 9 caractères .")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password min un lettre  (Majuscule).")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password min un lettre  (Minuscule).")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password min un nomber 1..9.")
        if not re.search(r'[@&]', value):
            raise serializers.ValidationError("Password  @ or &.")
        return value
    def create(self,validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = False 
        user.save()
        return user
    


