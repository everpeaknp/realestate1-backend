from rest_framework import serializers
from .models import Agent


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for agents"""
    
    social_media = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'email', 'phone', 'avatar', 'bio', 'quote',
            'specialties', 'social_media', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_avatar(self, obj):
        """Return uploaded image URL if available, otherwise fall back to URL field."""
        if obj.avatar_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar_image.url)
            return obj.avatar_image.url
        return obj.avatar or None

    def get_social_media(self, obj):
        """Return social media links as a dictionary"""
        return {
            'facebook': obj.facebook,
            'twitter': obj.twitter,
            'instagram': obj.instagram,
            'linkedin': obj.linkedin,
        }
