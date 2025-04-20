from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'type', 'price', 'description', 'image', 'discount', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 