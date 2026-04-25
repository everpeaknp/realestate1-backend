from django.contrib import admin
from django.utils.html import format_html
from .models import ContactCard, ContactFormSettings, ContactHeroSettings


@admin.register(ContactHeroSettings)
class ContactHeroSettingsAdmin(admin.ModelAdmin):
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
        return not ContactHeroSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False


@admin.register(ContactCard)
class ContactCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'value', 'icon', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'icon']
    search_fields = ['title', 'value']
    ordering = ['order', 'id']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('title', 'value', 'icon')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    actions = ['activate_cards', 'deactivate_cards']
    
    def activate_cards(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} contact card(s) activated.')
    activate_cards.short_description = 'Activate selected contact cards'
    
    def deactivate_cards(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} contact card(s) deactivated.')
    deactivate_cards.short_description = 'Deactivate selected contact cards'


@admin.register(ContactFormSettings)
class ContactFormSettingsAdmin(admin.ModelAdmin):
    list_display = ['agent_name', 'agent_title', 'image_preview', 'is_active']
    readonly_fields = ['image_preview']
    
    fieldsets = (
        ('Introduction', {
            'fields': ('intro_text',)
        }),
        ('Agent Information', {
            'fields': ('agent_name', 'agent_title', 'agent_image', 'image_preview')
        }),
        ('Social Media Links', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def image_preview(self, obj):
        """Display a preview of the agent image"""
        if obj.agent_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px; border-radius: 8px;" />',
                obj.agent_image.url
            )
        return "No image uploaded"
    image_preview.short_description = 'Image Preview'
    
    def has_add_permission(self, request):
        # Only allow one instance (singleton pattern)
        return not ContactFormSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False
