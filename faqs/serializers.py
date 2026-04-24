from rest_framework import serializers
from .models import FAQ, FAQsHeroSettings


class FAQsHeroSettingsSerializer(serializers.ModelSerializer):
    background_image = serializers.SerializerMethodField()
    background_url = serializers.SerializerMethodField()
    
    class Meta:
        model = FAQsHeroSettings
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


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQs"""
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
