from rest_framework import viewsets
from .models import Agent
from .serializers import AgentSerializer


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for agents (read-only for public)
    
    list: Get all active agents
    retrieve: Get single agent
    """
    
    queryset = Agent.objects.filter(is_active=True)
    serializer_class = AgentSerializer
