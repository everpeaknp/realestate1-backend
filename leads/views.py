from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .models import Lead, NewsletterSubscription
from .serializers import LeadSerializer, NewsletterSubscriptionSerializer


class LeadViewSet(viewsets.ModelViewSet):
    """
    API endpoint for leads/inquiries
    Supports both JSON and multipart/form-data for file uploads
    """
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    http_method_names = ['post', 'get']

    @action(detail=False, methods=['post'], url_path='contact')
    def contact(self, request):
        """Contact form submission endpoint"""
        data = request.data.copy()
        data['source'] = 'CONTACT_FORM'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='property-inquiry')
    def property_inquiry(self, request):
        """Property-specific inquiry endpoint"""
        data = request.data.copy()
        data['source'] = 'PROPERTY_INQUIRY'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='valuation')
    def valuation(self, request):
        """What's My Home Worth form submission"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Log incoming request details
            logger.info(f"Valuation request received - Content-Type: {request.content_type}")
            logger.info(f"Request data keys: {list(request.data.keys())}")
            logger.info(f"Request FILES keys: {list(request.FILES.keys())}")
            
            # For multipart/form-data, we need to handle data and files separately
            # request.data contains all form fields (including file field names)
            # request.FILES contains the actual file objects
            
            # Create a mutable copy of the data
            data = request.data.dict() if hasattr(request.data, 'dict') else dict(request.data)
            
            # Add files from request.FILES
            for key, file in request.FILES.items():
                data[key] = file
            
            # Ensure source and inquiry_type are set
            if 'source' not in data:
                data['source'] = 'VALUATION'
            if 'inquiry_type' not in data:
                data['inquiry_type'] = 'SELLING'
            
            logger.info(f"Processed data keys: {list(data.keys())}")
            
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                logger.error(f"Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            logger.info("Lead saved successfully")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.exception(f"Error in valuation endpoint: {str(e)}")
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NewsletterSubscriptionViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """
    POST /api/leads/newsletter/ — subscribe to newsletter.
    Handles duplicates: re-subscribes unsubscribed emails.
    """
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'email': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={'status': 'ACTIVE'}
        )

        if not created and subscription.status == 'UNSUBSCRIBED':
            subscription.status = 'ACTIVE'
            subscription.save()

        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
