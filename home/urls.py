from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HeroSettingsViewSet, HeroCardViewSet, HowItWorksStepViewSet,
    NeighborhoodViewSet, BenefitViewSet, BenefitGalleryImageViewSet,
    BenefitsSectionViewSet, ContactSectionSettingsViewSet,
    InstagramImageViewSet, PersonSectionSettingsViewSet, StatItemViewSet
)

router = DefaultRouter()
router.register(r'hero-settings', HeroSettingsViewSet, basename='hero-settings')
router.register(r'hero-cards', HeroCardViewSet, basename='hero-cards')
router.register(r'how-it-works', HowItWorksStepViewSet, basename='how-it-works')
router.register(r'neighborhoods', NeighborhoodViewSet, basename='neighborhoods')
router.register(r'benefits', BenefitViewSet, basename='benefits')
router.register(r'benefit-gallery', BenefitGalleryImageViewSet, basename='benefit-gallery')
router.register(r'benefits-section', BenefitsSectionViewSet, basename='benefits-section')
router.register(r'contact-section', ContactSectionSettingsViewSet, basename='contact-section')
router.register(r'instagram', InstagramImageViewSet, basename='instagram')
router.register(r'person-section', PersonSectionSettingsViewSet, basename='person-section')
router.register(r'stats', StatItemViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]
