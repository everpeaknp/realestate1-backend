from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import HomeWorthHeroSettings, HomeWorthFormSettings
from .serializers import HomeWorthHeroSettingsSerializer, HomeWorthFormSettingsSerializer


class HomeWorthHeroSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for home worth hero settings.
    Returns the singleton home worth hero settings.
    """
    queryset = HomeWorthHeroSettings.objects.filter(is_active=True)
    serializer_class = HomeWorthHeroSettingsSerializer
    permission_classes = [AllowAny]


class HomeWorthFormSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for home worth form settings.
    Returns the singleton home worth form settings.
    """
    queryset = HomeWorthFormSettings.objects.filter(is_active=True)
    serializer_class = HomeWorthFormSettingsSerializer
    permission_classes = [AllowAny]
