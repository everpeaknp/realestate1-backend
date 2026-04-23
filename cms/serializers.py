from rest_framework import serializers
from .models import HeaderSettings, NavigationLink, FooterSettings, FooterLink


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
