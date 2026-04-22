from rest_framework import serializers
from .models import Lead, NewsletterSubscription


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'inquiry_type', 'location', 'subject', 'message',
            'source', 'related_property', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = ['id', 'email', 'status', 'subscribed_at']
        read_only_fields = ['id', 'status', 'subscribed_at']
