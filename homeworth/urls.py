from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HomeWorthHeroSettingsViewSet, HomeWorthFormSettingsViewSet

router = DefaultRouter()
router.register(r'hero-settings', HomeWorthHeroSettingsViewSet, basename='homeworth-hero-settings')
router.register(r'form-settings', HomeWorthFormSettingsViewSet, basename='homeworth-form-settings')

urlpatterns = [
    path('', include(router.urls)),
]
