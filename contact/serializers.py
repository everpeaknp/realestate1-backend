from rest_framework import serializers
from .models import ContactCard, ContactFormSettings, ContactHeroSettings


class ContactHeroSettingsSerializer(serializers.ModelSerializer):
    background_image = serializers.SerializerMethodField()
    background_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactHeroSettings
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
