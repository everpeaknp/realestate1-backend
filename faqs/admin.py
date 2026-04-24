from django.contrib import admin
from django.utils.html import format_html
from .models import FAQ, FAQsHeroSettings


@admin.register(FAQsHeroSettings)
class FAQsHeroSettingsAdmin(admin.ModelAdmin):
    """Admin for FAQs Hero Settings (Singleton)"""
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
        return not FAQsHeroSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """Enhanced admin for FAQ model with Jazzmin optimization"""
    list_display = ('question_preview', 'category_badge', 'order', 'is_active_icon', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('question', 'answer')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('order',)
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('FAQ Content', {
            'fields': ('question', 'answer', 'category')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def question_preview(self, obj):
        preview = obj.question[:80] + '...' if len(obj.question) > 80 else obj.question
        return format_html('<span style="font-weight: 500;">{}</span>', preview)
    question_preview.short_description = 'Question'
    question_preview.admin_order_field = 'question'
    
    def category_badge(self, obj):
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.category
        )
    category_badge.short_description = 'Category'
    category_badge.admin_order_field = 'category'
    
    def is_active_icon(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #28a745; font-size: 18px;">✓</span>')
        return format_html('<span style="color: #dc3545; font-size: 18px;">✗</span>')
    is_active_icon.short_description = 'Active'
    is_active_icon.admin_order_field = 'is_active'
    
    actions = ['activate_faqs', 'deactivate_faqs']
    
    def activate_faqs(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} FAQs activated.', 'success')
    activate_faqs.short_description = '✓ Activate selected FAQs'
    
    def deactivate_faqs(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} FAQs deactivated.', 'warning')
    deactivate_faqs.short_description = '✗ Deactivate selected FAQs'
