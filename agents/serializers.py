from rest_framework import serializers
from .models import Agent


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for agents"""
    
    social_media = serializers.SerializerMethodField()
    
    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'email', 'phone', 'avatar', 'bio',
            'specialties', 'social_media', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_social_media(self, obj):
        """Return social media links as a dictionary"""
        return {
            'facebook': obj.facebook,
            'twitter': obj.twitter,
            'instagram': obj.instagram,
            'linkedin': obj.linkedin,
        }
