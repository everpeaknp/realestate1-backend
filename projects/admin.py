from django.contrib import admin
from django.utils.html import format_html
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Enhanced admin for Project model with Jazzmin optimization"""
    list_display = (
        'title', 'category_badge', 'location', 'completion_date', 
        'is_featured_icon', 'image_count_display', 'created_at'
    )
    list_filter = ('category', 'is_featured', 'completion_date', 'created_at')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'completion_date'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'is_featured')
        }),
        ('Location & Date', {
            'fields': ('location', 'completion_date')
        }),
        ('Images', {
            'fields': ('images',),
            'description': 'Enter image URLs as a JSON array, e.g., ["url1", "url2"]'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def category_badge(self, obj):
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.category
        )
    category_badge.short_description = 'Category'
    category_badge.admin_order_field = 'category'
    
    def is_featured_icon(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: #ffc107; font-size: 18px;">★</span>')
        return format_html('<span style="color: #ddd; font-size: 18px;">☆</span>')
    is_featured_icon.short_description = 'Featured'
    is_featured_icon.admin_order_field = 'is_featured'
    
    def image_count_display(self, obj):
        count = len(obj.images) if obj.images else 0
        color = '#28a745' if count > 0 else '#999'
        return format_html(
            '<span style="color: {};">📷 {} images</span>',
            color,
            count
        )
    image_count_display.short_description = 'Images'
    
    actions = ['mark_as_featured', 'remove_featured']
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} projects marked as featured.', 'success')
    mark_as_featured.short_description = '⭐ Mark as featured'
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} projects removed from featured.', 'success')
    remove_featured.short_description = '☆ Remove from featured'
