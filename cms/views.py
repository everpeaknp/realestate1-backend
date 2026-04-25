from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import (
    HeaderSettings, NavigationLink, FooterSettings, FooterLink, 
    NewsletterSettings, PropertySidebarSettings, PropertiesHeroSettings
)
from .serializers import (
    HeaderSettingsSerializer, NavigationLinkSerializer,
    FooterSettingsSerializer, FooterLinkSerializer, NewsletterSettingsSerializer,
    PropertySidebarSettingsSerializer, PropertiesHeroSettingsSerializer
)


class HeaderSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for header settings.
    Returns the singleton header settings with navigation links.
    """
    queryset = HeaderSettings.objects.filter(is_active=True)
    serializer_class = HeaderSettingsSerializer
    permission_classes = [AllowAny]


class NavigationLinkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for navigation links.
    Returns only active links ordered by the order field.
    """
    queryset = NavigationLink.objects.filter(is_active=True).order_by('order')
    serializer_class = NavigationLinkSerializer
    permission_classes = [AllowAny]


class FooterSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for footer settings.
    Returns the singleton footer settings with footer links.
    """
    queryset = FooterSettings.objects.filter(is_active=True)
    serializer_class = FooterSettingsSerializer
    permission_classes = [AllowAny]


class FooterLinkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for footer links.
    Returns only active links ordered by the order field.
    """
    queryset = FooterLink.objects.filter(is_active=True).order_by('order')
    serializer_class = FooterLinkSerializer
    permission_classes = [AllowAny]


class NewsletterSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for newsletter settings.
    Returns the singleton newsletter settings.
    """
    queryset = NewsletterSettings.objects.filter(is_active=True)
    serializer_class = NewsletterSettingsSerializer
    permission_classes = [AllowAny]


class PropertySidebarSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for property sidebar settings.
    Returns the singleton property sidebar settings with default agent.
    """
    queryset = PropertySidebarSettings.objects.filter(is_active=True)
    serializer_class = PropertySidebarSettingsSerializer
    permission_classes = [AllowAny]


class PropertiesHeroSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for properties hero settings.
    Returns the singleton properties hero settings.
    """
    queryset = PropertiesHeroSettings.objects.filter(is_active=True)
    serializer_class = PropertiesHeroSettingsSerializer
    permission_classes = [AllowAny]
