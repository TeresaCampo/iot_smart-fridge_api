from rest_framework import serializers
from .models import Fridge, Product,Parameter, CustomUser
from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    fridge_id = serializers.PrimaryKeyRelatedField(queryset=Fridge.objects.all(), source='fridge', required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'fridge_id']
        read_only_fields = ['email', 'fridge_id']
    
class CustomUserSignUpSerializer(serializers.Serializer):
    fridge_id = serializers.IntegerField()
    email = serializers.EmailField() 
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


    class Meta:
        fields = ['email', 'password', 'first_name', 'last_name', 'fridge_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Recuperiamo il fridge usando il fridge_id
        fridge_id = validated_data['fridge_id']
        try:
            fridge = Fridge.objects.get(fridge_id=fridge_id)
        except Fridge.DoesNotExist:
            raise serializers.ValidationError({'fridge_id': 'Invalid fridge ID'})

        # Creiamo l'utente
        user = CustomUser(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            fridge=fridge
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

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
