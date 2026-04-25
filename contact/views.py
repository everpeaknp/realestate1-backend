from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import ContactCard, ContactFormSettings, ContactHeroSettings
from .serializers import ContactCardSerializer, ContactFormSettingsSerializer, ContactHeroSettingsSerializer


class ContactHeroSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for contact hero settings.
    Returns the singleton contact hero settings.
    """
    queryset = ContactHeroSettings.objects.filter(is_active=True)
    serializer_class = ContactHeroSettingsSerializer
    permission_classes = [AllowAny]


class ContactCardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for contact cards.
    Returns only active cards ordered by the order field.
    """
    queryset = ContactCard.objects.filter(is_active=True).order_by('order')
    serializer_class = ContactCardSerializer
    permission_classes = [AllowAny]


class ContactFormSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for contact form settings.
    Returns the singleton settings instance.
    """
    queryset = ContactFormSettings.objects.filter(is_active=True)
    serializer_class = ContactFormSettingsSerializer
    permission_classes = [AllowAny]
