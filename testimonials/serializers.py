from rest_framework import serializers
from .models import Testimonial, TestimonialsHeroSettings


class TestimonialsHeroSettingsSerializer(serializers.ModelSerializer):
    background_image = serializers.SerializerMethodField()
    background_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TestimonialsHeroSettings
        fields = ['id', 'title', 'subtitle', 'background_image', 'background_url', 'background_image_url', 'is_active']
    
    def get_background_image(self, obj):
        if not obj.background_image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.background_image.url)
        return obj.background_image.url
    
    def get_background_url(self, obj):
        """Return the actual URL to use (uploaded image or fallback)"""
        if obj.background_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.background_image.url)
            return obj.background_image.url
        return obj.background_image_url


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
