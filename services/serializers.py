from rest_framework import serializers
from .models import Service, ServiceFeature


class ServiceFeatureSerializer(serializers.ModelSerializer):
    """Serializer for service features"""
    
    class Meta:
        model = ServiceFeature
        fields = ['id', 'text', 'order']


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for services"""
    
    features = ServiceFeatureSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'title', 'slug', 'description', 'image', 'layout',
            'phone', 'email', 'button_text', 'features', 'is_active',
            'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_image(self, obj):
        """Return full URL for image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
