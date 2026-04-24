from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Project, ProjectsHeroSettings
from .serializers import ProjectSerializer, ProjectsHeroSettingsSerializer


class ProjectsHeroSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for projects hero settings.
    Returns the singleton projects hero settings.
    """
    queryset = ProjectsHeroSettings.objects.filter(is_active=True).order_by('-updated_at')
    serializer_class = ProjectsHeroSettingsSerializer
    permission_classes = [AllowAny]


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for projects (read-only for public)
    
    list: Get all projects
    retrieve: Get single project
    featured: Get featured projects
    """
    
    queryset = Project.objects.prefetch_related('images').all()
    serializer_class = ProjectSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured projects"""
        projects = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all unique categories"""
        categories = Project.objects.values_list('category', flat=True).distinct()
        return Response({'categories': list(categories)})
