from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoalViewSet, ServicesProvideViewSet, AboutHeroSettingsViewSet

router = DefaultRouter()
router.register(r'hero-settings', AboutHeroSettingsViewSet, basename='about-hero-settings')
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'services-provide', ServicesProvideViewSet, basename='services-provide')

urlpatterns = [
    path('', include(router.urls)),
]
