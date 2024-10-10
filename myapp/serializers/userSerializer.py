from rest_framework import serializers
from django.contrib.auth.models import User
from myapp.Models import Client

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    is_staff = serializers.BooleanField(required=False, default=False)
    is_superuser = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class ClientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Directly accessing username through user

    class Meta:
        model = Client
        fields = ['id', 'username', 'additional_info']  # Adjust fields as necessary

def create(self, validated_data):
    user_data = validated_data.pop('user')
    user_serializer = UserCreateSerializer(data=user_data)
    if user_serializer.is_valid():
        user = user_serializer.save()  # Create User instance
        client = Client.objects.create(user=user, **validated_data)  # Create Client instance
        return client
    else:
        raise serializers.ValidationError(user_serializer.errors)  # Rai
    
# JWT Token Serializer remains unchanged
class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()

