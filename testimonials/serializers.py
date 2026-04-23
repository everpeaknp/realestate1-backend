from rest_framework import serializers
from .models import Testimonial


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for testimonials"""
    
    role = serializers.CharField(source='get_role_display')
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'title', 'text', 'name', 'role', 'image',
            'rating', 'video_url', 'is_featured', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_featured']
