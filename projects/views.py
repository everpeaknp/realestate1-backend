from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for projects (read-only for public)
    
    list: Get all projects
    retrieve: Get single project
    featured: Get featured projects
    """
    
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
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
