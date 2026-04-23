from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HeaderSettingsViewSet, NavigationLinkViewSet,
    FooterSettingsViewSet, FooterLinkViewSet
)

router = DefaultRouter()
router.register(r'header-settings', HeaderSettingsViewSet, basename='header-settings')
router.register(r'navigation-links', NavigationLinkViewSet, basename='navigation-links')
router.register(r'footer-settings', FooterSettingsViewSet, basename='footer-settings')
router.register(r'footer-links', FooterLinkViewSet, basename='footer-links')

urlpatterns = [
    path('', include(router.urls)),
]
