from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, PropertiesHeroSettingsViewSet
from .eagle_proxy import (
    eagle_properties_proxy,
    eagle_property_detail_proxy,
    eagle_test_auth_proxy,
)
from .reaxml_views import (
    reaxml_properties,
    reaxml_property_detail,
    reaxml_health,
)

router = DefaultRouter()
router.register(r'hero-settings', PropertiesHeroSettingsViewSet, basename='properties-hero-settings')
router.register(r'', PropertyViewSet, basename='property')

urlpatterns = [
    # Eagle API proxy routes (must come before router.urls)
    path('eagle/properties/', eagle_properties_proxy, name='eagle-properties-proxy'),
    path('eagle/properties/<str:property_id>/', eagle_property_detail_proxy, name='eagle-property-detail-proxy'),
    path('eagle/test-auth/', eagle_test_auth_proxy, name='eagle-test-auth-proxy'),
    path('reaxml/properties/', reaxml_properties, name='reaxml-properties'),
    path('reaxml/properties/<str:property_id>/', reaxml_property_detail, name='reaxml-property-detail'),
    path('reaxml/health/', reaxml_health, name='reaxml-health'),
    
    # Regular property routes
    path('', include(router.urls)),
]
