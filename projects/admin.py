from django.contrib import admin
from django.utils.html import format_html
from .models import Project, ProjectImage


# Don't register Project model - only manage through ProjectImage
# @admin.register(Project)


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    """Admin for project images - main interface for managing projects"""
    list_display = ('project', 'title', 'order', 'image_preview', 'created_at')
    list_filter = ('project', 'created_at')
    search_fields = ('title', 'caption', 'project__title')
    list_editable = ('order',)
    readonly_fields = ('image_preview', 'created_at')
    exclude = ('project',)  # Hide project field from form
    
    fieldsets = (
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
