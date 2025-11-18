from rest_framework import serializers
from .models import GsList, Zone, Owner, Product


class GsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GsList
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = '__all__'


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']