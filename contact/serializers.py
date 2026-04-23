from rest_framework import serializers
from .models import ContactCard, ContactFormSettings


class ContactCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactCard
        fields = ['id', 'title', 'value', 'icon', 'order', 'is_active']


class ContactFormSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactFormSettings
        fields = [
            'id', 'intro_text', 'agent_name', 'agent_title', 'agent_image',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'is_active'
        ]
