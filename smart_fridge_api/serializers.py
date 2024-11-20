from rest_framework import serializers
from .models import Fridge, Product

class FridgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fridge
        fields = ['fridge_id', 'address', 'city', 'country']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['fridge', 'barcode', 'expire_date', 'name']

