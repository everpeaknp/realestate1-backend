from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import FAQ, FAQsHeroSettings
from .serializers import FAQSerializer, FAQsHeroSettingsSerializer


class FAQsHeroSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for FAQs hero settings.
    Returns the singleton FAQs hero settings.
    """
    queryset = FAQsHeroSettings.objects.filter(is_active=True).order_by('-updated_at')
    serializer_class = FAQsHeroSettingsSerializer
    permission_classes = [AllowAny]


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for FAQs (read-only for public)
    
    list: Get all active FAQs
    retrieve: Get single FAQ
    categories: Get all unique categories
    """
    
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all unique categories"""
        categories = FAQ.objects.filter(
            is_active=True
        ).values_list('category', flat=True).distinct()
        return Response({'categories': list(categories)})
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get FAQs grouped by category"""
        category = request.query_params.get('category')
        if category:
            faqs = self.queryset.filter(category=category)
        else:
            faqs = self.queryset
        
        serializer = self.get_serializer(faqs, many=True)
        return Response(serializer.data)
