from rest_framework import serializers
from .models import HomeWorthHeroSettings, HomeWorthFormSettings


class HomeWorthHeroSettingsSerializer(serializers.ModelSerializer):
    background_image = serializers.SerializerMethodField()
    background_url = serializers.SerializerMethodField()
    
    class Meta:
        model = HomeWorthHeroSettings
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


class HomeWorthFormSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeWorthFormSettings
        fields = [
            'id', 'form_title', 'form_description', 'submit_button_text',
            'success_message', 'is_active'
        ]
