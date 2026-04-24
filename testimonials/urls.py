from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestimonialViewSet, TestimonialsHeroSettingsViewSet

router = DefaultRouter()
router.register(r'hero', TestimonialsHeroSettingsViewSet, basename='testimonials-hero')
router.register(r'', TestimonialViewSet, basename='testimonial')

urlpatterns = [
    path('', include(router.urls)),
]
