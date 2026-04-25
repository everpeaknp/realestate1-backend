from django.contrib import admin
from django.utils.html import format_html
from .models import HomeWorthHeroSettings, HomeWorthFormSettings


@admin.register(HomeWorthHeroSettings)
class HomeWorthHeroSettingsAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'image_preview', 'is_active']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Hero Content', {
            'fields': ('title', 'subtitle')
        }),
        ('Background Image', {
            'fields': ('background_image', 'image_preview', 'background_image_url'),
            'description': 'Upload an image or provide a URL. Uploaded image takes priority.'
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def image_preview(self, obj):
        """Display a preview of the background image"""
        if obj.background_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 400px; border-radius: 8px;" />',
                obj.background_image.url
            )
        elif obj.background_image_url:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 400px; border-radius: 8px;" /><br/><small>Using fallback URL</small>',
                obj.background_image_url
            )
        return "No image"
    image_preview.short_description = 'Background Preview'
    
    def has_add_permission(self, request):
        # Only allow one instance (singleton pattern)
        return not HomeWorthHeroSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False


@admin.register(HomeWorthFormSettings)
class HomeWorthFormSettingsAdmin(admin.ModelAdmin):
    list_display = ['form_title', 'submit_button_text', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Form Content', {
            'fields': ('form_title', 'form_description', 'submit_button_text')
        }),
        ('Messages', {
            'fields': ('success_message',),
            'description': 'Customize messages shown to users'
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance (singleton pattern)
        return not HomeWorthFormSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False
