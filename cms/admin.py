from django.contrib import admin
from .models import HeaderSettings, NavigationLink, FooterSettings, FooterLink


@admin.register(HeaderSettings)
class HeaderSettingsAdmin(admin.ModelAdmin):
    list_display = ['logo_text', 'phone_number', 'is_active']
    
    fieldsets = (
        ('Logo & Branding', {
            'fields': ('logo_image', 'logo_text')
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance (singleton pattern)
        return not HeaderSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False


@admin.register(NavigationLink)
class NavigationLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'href', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'href']
    ordering = ['order', 'id']
    
    fieldsets = (
        ('Link Information', {
            'fields': ('name', 'href')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    actions = ['activate_links', 'deactivate_links']
    
    def activate_links(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} navigation link(s) activated.')
    activate_links.short_description = 'Activate selected navigation links'
    
    def deactivate_links(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} navigation link(s) deactivated.')
    deactivate_links.short_description = 'Deactivate selected navigation links'


@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    list_display = ['logo_text', 'phone_number', 'email', 'is_active']
    
    fieldsets = (
        ('Logo & Branding', {
            'fields': ('logo_image', 'logo_text')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Social Media Links', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url')
        }),
        ('Copyright', {
            'fields': ('copyright_text',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance (singleton pattern)
        return not FooterSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False


@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'href', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'href']
    ordering = ['order', 'id']
    
    fieldsets = (
        ('Link Information', {
            'fields': ('name', 'href')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    actions = ['activate_links', 'deactivate_links']
    
    def activate_links(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} footer link(s) activated.')
    activate_links.short_description = 'Activate selected footer links'
    
    def deactivate_links(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} footer link(s) deactivated.')
    deactivate_links.short_description = 'Deactivate selected footer links'
