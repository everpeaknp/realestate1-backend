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
        # Handle both JSON and multipart/form-data
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # Ensure source and inquiry_type are set
        if 'source' not in data:
            data['source'] = 'VALUATION'
        if 'inquiry_type' not in data:
            data['inquiry_type'] = 'SELLING'
        
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
