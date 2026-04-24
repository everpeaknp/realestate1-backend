from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FAQViewSet, FAQsHeroSettingsViewSet

router = DefaultRouter()
router.register(r'hero', FAQsHeroSettingsViewSet, basename='faqs-hero')
router.register(r'', FAQViewSet, basename='faq')

urlpatterns = [
    path('', include(router.urls)),
]
