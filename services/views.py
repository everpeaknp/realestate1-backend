from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Service
from .serializers import ServiceSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for services (read-only for public)
    
    list: Get all active services
    retrieve: Get single service by slug
    """
    
    queryset = Service.objects.filter(is_active=True).prefetch_related('features')
    serializer_class = ServiceSerializer
    lookup_field = 'slug'
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
