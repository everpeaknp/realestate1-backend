from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Goal, ServicesProvide, AboutHeroSettings
from .serializers import GoalSerializer, ServicesProvideSerializer, AboutHeroSettingsSerializer


class AboutHeroSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for about hero settings.
    Returns the singleton about hero settings.
    """
    queryset = AboutHeroSettings.objects.filter(is_active=True)
    serializer_class = AboutHeroSettingsSerializer
    permission_classes = [AllowAny]


class GoalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for goals (read-only for public)
    
    list: Get all active goals
    """
    
    queryset = Goal.objects.filter(is_active=True)
    serializer_class = GoalSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ServicesProvideViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for services provide section (read-only for public)
    
    list: Get the services provide section
    """
    
    queryset = ServicesProvide.objects.filter(is_active=True)
    serializer_class = ServicesProvideSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
