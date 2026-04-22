from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Property
from .serializers import PropertyListSerializer, PropertyDetailSerializer


class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for properties
    
    list: Get all properties
    retrieve: Get single property by slug
    featured: Get featured properties only
    search: Search properties with filters
    """
    queryset = Property.objects.filter(status='AVAILABLE')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'status', 'city', 'state', 'is_featured']
    search_fields = ['title', 'description', 'city', 'state', 'address']
    ordering_fields = ['price', 'created_at', 'sqft', 'beds']
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PropertyDetailSerializer
        return PropertyListSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured properties"""
        featured_properties = self.queryset.filter(is_featured=True)[:4]
        serializer = self.get_serializer(featured_properties, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def for_sale(self, request):
        """Get properties for sale"""
        properties = self.queryset.filter(property_type='FOR_SALE')
        page = self.paginate_queryset(properties)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def for_rent(self, request):
        """Get properties for rent"""
        properties = self.queryset.filter(property_type='FOR_RENT')
        page = self.paginate_queryset(properties)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
