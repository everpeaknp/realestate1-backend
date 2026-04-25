from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, PropertiesHeroSettingsViewSet

router = DefaultRouter()
router.register(r'hero-settings', PropertiesHeroSettingsViewSet, basename='properties-hero-settings')
router.register(r'', PropertyViewSet, basename='property')

urlpatterns = [
    path('', include(router.urls)),
]
