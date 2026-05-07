from django.contrib import admin
from .models import Service, ServiceFeature, ServicesHeroSettings


class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1
    fields = ['text', 'order']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'layout', 'is_active', 'order']
    list_filter = ['is_active', 'layout']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceFeatureInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Image', {
            'fields': ('image', 'image_url'),
            'description': 'Upload an image or provide an external URL. Uploaded image takes priority.'
        }),
        ('Layout & Display', {
            'fields': ('layout', 'order', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'button_text')
        }),
    )


@admin.register(ServicesHeroSettings)
class ServicesHeroSettingsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'updated_at']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle')
        }),
        ('Background Image', {
            'fields': ('background_image', 'background_url'),
            'description': 'Upload an image or provide an external URL. Uploaded image takes priority.'
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one hero settings instance
        return not ServicesHeroSettings.objects.exists()
