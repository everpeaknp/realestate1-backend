from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    HeroSettings, HeroCard, HowItWorksStep, Neighborhood,
    Benefit, BenefitGalleryImage, BenefitsSection,
    ContactSectionSettings, InstagramImage, PersonSectionSettings, StatItem
)
from .serializers import (
    HeroSettingsSerializer, HeroCardSerializer, HowItWorksStepSerializer,
    NeighborhoodSerializer, BenefitSerializer, BenefitGalleryImageSerializer,
    BenefitsSectionSerializer, ContactSectionSettingsSerializer,
    InstagramImageSerializer, PersonSectionSettingsSerializer, StatItemSerializer
)


class HeroSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for hero settings (singleton)
    """
    queryset = HeroSettings.objects.filter(is_active=True)
    serializer_class = HeroSettingsSerializer

    def list(self, request, *args, **kwargs):
        instance = self.queryset.first()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({}, status=status.HTTP_200_OK)


class HeroCardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for hero cards
    """
    queryset = HeroCard.objects.filter(is_active=True)
    serializer_class = HeroCardSerializer


class HowItWorksStepViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for how it works steps
    """
    queryset = HowItWorksStep.objects.filter(is_active=True)
    serializer_class = HowItWorksStepSerializer


class NeighborhoodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for neighborhoods
    """
    queryset = Neighborhood.objects.filter(is_active=True)
    serializer_class = NeighborhoodSerializer


class BenefitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for benefits
    """
    queryset = Benefit.objects.filter(is_active=True)
    serializer_class = BenefitSerializer


class BenefitGalleryImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for benefit gallery images
    """
    queryset = BenefitGalleryImage.objects.filter(is_active=True)
    serializer_class = BenefitGalleryImageSerializer


class BenefitsSectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for benefits section (singleton)
    """
    queryset = BenefitsSection.objects.filter(is_active=True)
    serializer_class = BenefitsSectionSerializer

    def list(self, request, *args, **kwargs):
        instance = self.queryset.first()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({}, status=status.HTTP_200_OK)


class ContactSectionSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for contact section settings (singleton)
    """
    queryset = ContactSectionSettings.objects.filter(is_active=True)
    serializer_class = ContactSectionSettingsSerializer

    def list(self, request, *args, **kwargs):
        instance = self.queryset.first()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({}, status=status.HTTP_200_OK)


class InstagramImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for instagram images
    """
    queryset = InstagramImage.objects.filter(is_active=True)
    serializer_class = InstagramImageSerializer


class PersonSectionSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for person section settings (singleton)
    """
    queryset = PersonSectionSettings.objects.filter(is_active=True)
    serializer_class = PersonSectionSettingsSerializer

    def list(self, request, *args, **kwargs):
        instance = self.queryset.first()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({}, status=status.HTTP_200_OK)


class StatItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for stat items
    """
    queryset = StatItem.objects.filter(is_active=True)
    serializer_class = StatItemSerializer
