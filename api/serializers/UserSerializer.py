
from rest_framework import serializers

from api.model.UserModel import User
from django.contrib.auth.hashers import make_password

# 1. User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nombre', 'email', 'is_staff', 'date_joined', 'updated_at', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # Cifrar contraseña
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)





