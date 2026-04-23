from django.contrib import admin
from django.utils.html import format_html
from .models import Goal, ServicesProvide


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    """Admin for Goal model"""
    list_display = ('title', 'description_preview', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active')
    
    fieldsets = (
        ('Goal Information', {
            'fields': ('title', 'description', 'is_active', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def description_preview(self, obj):
        """Show truncated description"""
        if len(obj.description) > 60:
            return f"{obj.description[:60]}..."
        return obj.description
    description_preview.short_description = 'Description'
    
    actions = ['activate_goals', 'deactivate_goals']
    
    def activate_goals(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} goals activated.', 'success')
    activate_goals.short_description = '✓ Activate selected goals'
    
    def deactivate_goals(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} goals deactivated.', 'success')
    deactivate_goals.short_description = '✗ Deactivate selected goals'


@admin.register(ServicesProvide)
class ServicesProvideAdmin(admin.ModelAdmin):
    """Admin for ServicesProvide model (singleton)"""
    list_display = ('__str__', 'subtitle', 'title_preview', 'is_active', 'image_preview')
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Content', {
            'fields': ('subtitle', 'title', 'is_active')
        }),
        ('Background Image', {
            'fields': ('background_image', 'image_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_preview(self, obj):
        """Show truncated title"""
        if len(obj.title) > 60:
            return f"{obj.title[:60]}..."
        return obj.title
    title_preview.short_description = 'Title'
    
    def image_preview(self, obj):
        if obj.background_image:
            return format_html(
                '<img src="{}" style="max-height: 150px; max-width: 300px; object-fit: cover; border-radius: 4px;" />',
                obj.background_image.url
            )
        return '-'
    image_preview.short_description = 'Preview'
    
    def has_add_permission(self, request):
        # Only allow adding if no instance exists
        return not ServicesProvide.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
