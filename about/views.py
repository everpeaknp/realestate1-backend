from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Goal, ServicesProvide
from .serializers import GoalSerializer, ServicesProvideSerializer


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
