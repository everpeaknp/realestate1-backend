from rest_framework import serializers
from .models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQs"""
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
