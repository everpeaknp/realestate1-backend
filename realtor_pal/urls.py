from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from leads.urls import newsletter_urlpatterns
from properties.eagle_proxy import (
    eagle_properties_proxy,
    eagle_property_detail_proxy,
    eagle_test_auth_proxy,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # CKEditor upload URLs (required for RichTextUploadingField)
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # Eagle API proxy routes (must come before other API routes)
    path('api/eagle/properties/', eagle_properties_proxy, name='eagle-properties-proxy'),
    path('api/eagle/properties/<str:property_id>/', eagle_property_detail_proxy, name='eagle-property-detail-proxy'),
    path('api/eagle/test-auth/', eagle_test_auth_proxy, name='eagle-test-auth-proxy'),

    # API endpoints
    path('api/properties/', include('properties.urls')),
    path('api/leads/', include('leads.urls')),
    path('api/newsletter/', include((newsletter_urlpatterns, 'newsletter'))),
    path('api/blog/', include('blog.urls')),
    path('api/testimonials/', include('testimonials.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/faqs/', include('faqs.urls')),
    path('api/agents/', include('agents.urls')),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/services/', include('services.urls')),
    path('api/about/', include('about.urls')),
    path('api/contact/', include('contact.urls')),
    path('api/cms/', include('cms.urls')),
    path('api/home/', include('home.urls')),
    path('api/homeworth/', include('homeworth.urls')),
    path('api/homeworth/', include('homeworth.urls')),

    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in both development and production
# In production, this is necessary when using Docker without a separate media server
urlpatterns += [
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
