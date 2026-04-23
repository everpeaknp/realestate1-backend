from rest_framework import serializers
from .models import Goal, ServicesProvide


class GoalSerializer(serializers.ModelSerializer):
    """Serializer for goals"""
    
    class Meta:
        model = Goal
        fields = ['id', 'title', 'description', 'order', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ServicesProvideSerializer(serializers.ModelSerializer):
    """Serializer for services provide section"""
    
    background_image = serializers.SerializerMethodField()
    
    class Meta:
        model = ServicesProvide
        fields = ['id', 'subtitle', 'title', 'background_image', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_background_image(self, obj):
        """Return full URL for background image"""
        if obj.background_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.background_image.url)
            return obj.background_image.url
        return None
