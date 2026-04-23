from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from leads.urls import newsletter_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # CKEditor upload URLs (required for RichTextUploadingField)
    path('ckeditor/', include('ckeditor_uploader.urls')),

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

    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
