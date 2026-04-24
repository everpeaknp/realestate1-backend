from django.contrib import admin
from django.utils.html import format_html
from .models import Project, ProjectImage, ProjectsHeroSettings


@admin.register(ProjectsHeroSettings)
class ProjectsHeroSettingsAdmin(admin.ModelAdmin):
    """Admin for Projects Hero Settings (Singleton)"""
    list_display = ('title', 'subtitle', 'is_active', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'background_preview')
    
    fieldsets = (
        ('Hero Content', {
            'fields': ('title', 'subtitle')
        }),
        ('Background Image', {
            'fields': ('background_image', 'background_image_url', 'background_preview'),
            'description': 'Upload an image or provide a URL. Uploaded image takes priority.'
        }),
        ('Display Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def background_preview(self, obj):
        url = obj.background_url
        if url:
            return format_html(
                '<img src="{}" style="max-width: 600px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                url
            )
        return format_html('<p style="color: #999;">No background image</p>')
    background_preview.short_description = 'Background Preview'
    
    def has_add_permission(self, request):
        # Only allow one instance (singleton)
        return not ProjectsHeroSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False


class ProjectImageInline(admin.TabularInline):
    """Inline admin for project images"""
    model = ProjectImage
    extra = 1
    fields = ('image', 'title', 'caption', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin for projects with inline images"""
    list_display = ('title', 'location', 'category', 'completion_date', 'is_featured', 'order')
    list_filter = ('category', 'is_featured', 'completion_date')
    search_fields = ('title', 'description', 'location')
    list_editable = ('is_featured', 'order')
    date_hierarchy = 'completion_date'
    inlines = [ProjectImageInline]
    
    fieldsets = (
        ('Project Information', {
            'fields': ('title', 'description', 'location', 'completion_date')
        }),
        ('Categorization', {
            'fields': ('category', 'is_featured', 'order')
        }),
    )


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    """Admin for project images - can also be managed individually"""
    list_display = ('project', 'title', 'order', 'image_preview', 'created_at')
    list_filter = ('project', 'created_at')
    search_fields = ('title', 'caption', 'project__title')
    list_editable = ('order',)
    readonly_fields = ('image_preview', 'created_at')
    
    fieldsets = (
        ('Project', {
            'fields': ('project',)
        }),
        ('Image Details', {
            'fields': ('image', 'image_preview', 'title', 'caption', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview'
