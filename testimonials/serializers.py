from rest_framework import serializers
from .models import Testimonial


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for testimonials"""
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'client_name', 'client_avatar', 'rating',
            'content', 'property_type', 'video_url',
            'is_featured', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_featured']
