from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactCardViewSet, ContactFormSettingsViewSet

router = DefaultRouter()
router.register(r'cards', ContactCardViewSet, basename='contact-cards')
router.register(r'form-settings', ContactFormSettingsViewSet, basename='contact-form-settings')

urlpatterns = [
    path('', include(router.urls)),
]
