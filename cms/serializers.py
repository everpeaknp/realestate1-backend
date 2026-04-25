from rest_framework import serializers
from .models import (
    HeaderSettings, NavigationLink, FooterSettings, FooterLink, 
    NewsletterSettings, PropertySidebarSettings, PropertiesHeroSettings
)


class NavigationLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavigationLink
        fields = ['id', 'name', 'href', 'order', 'is_active']


class HeaderSettingsSerializer(serializers.ModelSerializer):
    navigation_links = serializers.SerializerMethodField()
    logo_image = serializers.SerializerMethodField()
    
    class Meta:
        model = HeaderSettings
        fields = ['id', 'logo_image', 'logo_text', 'phone_number', 'is_active', 'navigation_links']
    
    def get_logo_image(self, obj):
        if obj.logo_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo_image.url)
            return obj.logo_image.url
        return None
    
    def get_navigation_links(self, obj):
        links = NavigationLink.objects.filter(is_active=True).order_by('order')
        return NavigationLinkSerializer(links, many=True).data


class FooterLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterLink
        fields = ['id', 'name', 'href', 'order', 'is_active']


class FooterSettingsSerializer(serializers.ModelSerializer):
    footer_links = serializers.SerializerMethodField()
    logo_image = serializers.SerializerMethodField()
    
    class Meta:
        model = FooterSettings
        fields = [
            'id', 'logo_image', 'logo_text', 'phone_number', 'email', 'copyright_text',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url',
            'is_active', 'footer_links'
        ]
    
    def get_logo_image(self, obj):
        if obj.logo_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo_image.url)
            return obj.logo_image.url
        return None
    
    def get_footer_links(self, obj):
        links = FooterLink.objects.filter(is_active=True).order_by('order')
        return FooterLinkSerializer(links, many=True).data


class NewsletterSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSettings
        fields = ['id', 'title', 'description', 'is_active']


class PropertySidebarSettingsSerializer(serializers.ModelSerializer):
    default_agent = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertySidebarSettings
        fields = ['id', 'form_title', 'default_agent', 'is_active']
    
    def get_default_agent(self, obj):
        if obj.default_agent:
            return {
                'id': obj.default_agent.id,
                'name': obj.default_agent.name,
                'email': obj.default_agent.email,
                'phone': obj.default_agent.phone,
                'avatar': obj.default_agent.avatar,
                'bio': obj.default_agent.bio,
            }
        return None


class PropertiesHeroSettingsSerializer(serializers.ModelSerializer):
    background_image = serializers.SerializerMethodField()
    background_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertiesHeroSettings
        fields = ['id', 'title', 'subtitle', 'background_image', 'background_url', 'background_image_url', 'is_active']
    
    def get_background_image(self, obj):
        if obj.background_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.background_image.url)
            return obj.background_image.url
        return None
    
    def get_background_url(self, obj):
        """Return the actual URL to use (uploaded image or fallback URL)"""
        if obj.background_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.background_image.url)
            return obj.background_image.url
        return obj.background_image_url
