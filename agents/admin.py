from django.contrib import admin
from django.utils.html import format_html
from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    """Enhanced admin for Agent model with Jazzmin optimization"""
    list_display = (
        'name', 'email', 'phone', 'is_active_icon', 
        'property_count', 'specialty_count_display', 'social_links', 'created_at'
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email', 'phone', 'bio')
    readonly_fields = ('created_at', 'updated_at', 'avatar_preview')
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'is_active')
        }),
        ('Profile', {
            'fields': ('avatar', 'avatar_preview', 'bio', 'specialties')
        }),
        ('Social Media', {
            'fields': ('facebook', 'twitter', 'instagram', 'linkedin'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height: 150px; max-width: 150px; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.avatar
            )
        return format_html('<p style="color: #999;">No avatar</p>')
    avatar_preview.short_description = 'Avatar Preview'
    
    def is_active_icon(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #28a745; font-size: 18px;">✓</span>')
        return format_html('<span style="color: #dc3545; font-size: 18px;">✗</span>')
    is_active_icon.short_description = 'Active'
    is_active_icon.admin_order_field = 'is_active'
    
    def property_count(self, obj):
        count = obj.properties.count()
        if count > 0:
            return format_html(
                '<a href="/admin/properties/property/?agent__id__exact={}" style="color: #007bff; text-decoration: none;">🏠 {} properties</a>',
                obj.id,
                count
            )
        return format_html('<span style="color: #999;">0 properties</span>')
    property_count.short_description = 'Properties'
    
    def specialty_count_display(self, obj):
        count = len(obj.specialties) if obj.specialties else 0
        return format_html('<span style="color: #17a2b8;">📋 {} specialties</span>', count)
    specialty_count_display.short_description = 'Specialties'
    
    def social_links(self, obj):
        links = []
        if obj.facebook:
            links.append('<a href="{}" target="_blank" style="margin-right: 5px; color: #3b5998;">FB</a>'.format(obj.facebook))
        if obj.twitter:
            links.append('<a href="{}" target="_blank" style="margin-right: 5px; color: #1da1f2;">TW</a>'.format(obj.twitter))
        if obj.instagram:
            links.append('<a href="{}" target="_blank" style="margin-right: 5px; color: #e1306c;">IG</a>'.format(obj.instagram))
        if obj.linkedin:
            links.append('<a href="{}" target="_blank" style="margin-right: 5px; color: #0077b5;">LI</a>'.format(obj.linkedin))
        return format_html(' | '.join(links)) if links else format_html('<span style="color: #999;">-</span>')
    social_links.short_description = 'Social Media'
    
    actions = ['activate_agents', 'deactivate_agents']
    
    def activate_agents(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} agents activated.', 'success')
    activate_agents.short_description = '✓ Activate selected agents'
    
    def deactivate_agents(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} agents deactivated.', 'warning')
    deactivate_agents.short_description = '✗ Deactivate selected agents'
