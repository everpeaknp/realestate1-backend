from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Lead, NewsletterSubscription
from .serializers import LeadSerializer, NewsletterSubscriptionSerializer


class LeadViewSet(viewsets.ModelViewSet):
    """
    API endpoint for leads/inquiries
    """
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
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
        data = request.data.copy()
        data['source'] = 'VALUATION'
        data.setdefault('inquiry_type', 'SELLING')
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
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
