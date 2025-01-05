from rest_framework import serializers
from .models import LaptopPost

class LaptopPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaptopPost
        fields = '__all__'
