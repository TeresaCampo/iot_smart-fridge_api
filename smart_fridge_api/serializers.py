from rest_framework import serializers
from .models import Fridge, Product,Parameter, UserProfile
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserProfileSignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    email = serializers.EmailField()
    fridge_id = serializers.IntegerField()

    class Meta:
        fields = ['username','password','email','fridge_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Creare l'utente
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        # Recuperare l'oggetto Fridge
        try:
            fridge = Fridge.objects.get(fridge_id=validated_data['fridge_id'])
        except Fridge.DoesNotExist:
            raise serializers.ValidationError({'fridge_id': 'Invalid fridge ID'})

        # Creare il profilo utente
        user_profile = UserProfile(user=user, fridge=fridge)
        user_profile.save()
        return user_profile
    
class FridgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fridge
        fields = ['fridge_id', 'address', 'city', 'country']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['fridge', 'barcode', 'expire_date', 'name']

class ParameterSerializer(serializers.ModelSerializer):
    sampling_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M")

    class Meta:
        model = Parameter
        fields = ['fridge','humidity','temperature','sampling_date'] 
