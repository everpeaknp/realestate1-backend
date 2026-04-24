from rest_framework import serializers
from .models import ContactCard, ContactFormSettings


class ContactCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactCard
        fields = ['id', 'title', 'value', 'icon', 'order', 'is_active']


class ContactFormSettingsSerializer(serializers.ModelSerializer):
    agent_image = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactFormSettings
        fields = [
            'id', 'intro_text', 'agent_name', 'agent_title', 'agent_image',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'is_active'
        ]
    
    def get_agent_image(self, obj):
        """Return the full URL for the agent image"""
        if obj.agent_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.agent_image.url)
            return obj.agent_image.url
        return None
