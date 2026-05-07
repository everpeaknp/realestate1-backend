from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, ServicesHeroSettingsViewSet

# Create separate routers to avoid conflicts
service_router = DefaultRouter()
service_router.register(r'', ServiceViewSet, basename='service')

hero_router = DefaultRouter()
hero_router.register(r'', ServicesHeroSettingsViewSet, basename='services-hero')

urlpatterns = [
    path('hero/', include(hero_router.urls)),
    path('', include(service_router.urls)),
]
