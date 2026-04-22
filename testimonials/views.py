from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Testimonial
from .serializers import TestimonialSerializer


class TestimonialViewSet(viewsets.ModelViewSet):
    """
    ViewSet for testimonials
    
    list: Get all approved testimonials
    retrieve: Get single testimonial
    create: Submit a new testimonial (pending approval)
    """
    
    queryset = Testimonial.objects.filter(is_approved=True)
    serializer_class = TestimonialSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured testimonials"""
        testimonials = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(testimonials, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def video(self, request):
        """Get video testimonials"""
        testimonials = self.queryset.exclude(video_url__isnull=True).exclude(video_url='')
        serializer = self.get_serializer(testimonials, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create a new testimonial (will be pending approval)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {
                'message': 'Testimonial submitted successfully. It will be visible after approval.',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
