from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Service, ServicesHeroSettings
from .serializers import ServiceSerializer, ServicesHeroSettingsSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for services (Buy, Sell, Rent, Home Loan)
    """
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class ServicesHeroSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for services hero settings
    """
    queryset = ServicesHeroSettings.objects.filter(is_active=True)
    serializer_class = ServicesHeroSettingsSerializer
    permission_classes = [AllowAny]
