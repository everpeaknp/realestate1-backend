from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import ContactCard, ContactFormSettings
from .serializers import ContactCardSerializer, ContactFormSettingsSerializer


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
