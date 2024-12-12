from rest_framework import serializers
from .models import Fridge, Product,Parameter
from django.utils import timezone
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
