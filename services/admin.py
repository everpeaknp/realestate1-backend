from django.contrib import admin
from django.utils.html import format_html
from .models import Service, ServiceFeature


class ServiceFeatureInline(admin.TabularInline):
    """Inline admin for service features"""
    model = ServiceFeature
    extra = 1
    fields = ('text', 'order')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin for Service model"""
    list_display = (
        'title', 'slug', 'layout_badge', 'is_active', 
        'feature_count', 'order', 'image_preview'
    )
    list_filter = ('is_active', 'layout', 'created_at')
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    list_editable = ('order', 'is_active')
    inlines = [ServiceFeatureInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'is_active', 'order')
        }),
        ('Visual & Layout', {
            'fields': ('image', 'image_preview', 'layout')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'button_text')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def layout_badge(self, obj):
        colors = {
            'IMAGE_LEFT': '#17a2b8',
            'IMAGE_RIGHT': '#6f42c1',
        }
        color = colors.get(obj.layout, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_layout_display()
        )
    layout_badge.short_description = 'Layout'
    layout_badge.admin_order_field = 'layout'
    
    def is_active_icon(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #28a745; font-size: 18px;">✓</span>')
        return format_html('<span style="color: #dc3545; font-size: 18px;">✗</span>')
    is_active_icon.short_description = 'Active'
    is_active_icon.admin_order_field = 'is_active'
    
    def feature_count(self, obj):
        count = obj.features.count()
        color = '#28a745' if count > 0 else '#999'
        return format_html(
            '<span style="color: {};">✓ {} features</span>',
            color,
            count
        )
    feature_count.short_description = 'Features'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 150px; max-width: 200px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview'
    
    actions = ['activate_services', 'deactivate_services']
    
    def activate_services(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} services activated.', 'success')
    activate_services.short_description = '✓ Activate selected services'
    
    def deactivate_services(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} services deactivated.', 'success')
    deactivate_services.short_description = '✗ Deactivate selected services'
