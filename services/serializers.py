from rest_framework import serializers
from .models import Service, ServiceFeature, ServicesHeroSettings


class ServiceFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFeature
        fields = ['id', 'text', 'order']


class ServiceSerializer(serializers.ModelSerializer):
    features = ServiceFeatureSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'title', 'slug', 'description', 'image', 
            'layout', 'phone', 'email', 'button_text', 
            'features', 'is_active', 'order'
        ]
    
    def get_image(self, obj):
        """Return the appropriate image URL"""
        request = self.context.get('request')
        if obj.image:
            # Return full URL for uploaded images
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        # Return full URL for external images
        return obj.image_url


class ServicesHeroSettingsSerializer(serializers.ModelSerializer):
    background_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ServicesHeroSettings
        fields = ['id', 'title', 'subtitle', 'background_url', 'is_active']
    
    def get_background_url(self, obj):
        """Return the appropriate background image URL"""
        request = self.context.get('request')
        if obj.background_image:
            # Return full URL for uploaded images
            if request:
                return request.build_absolute_uri(obj.background_image.url)
            return obj.background_image.url
        # Return full URL for external images
        return obj.background_url
