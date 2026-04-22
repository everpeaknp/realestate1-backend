from django.contrib import admin
from django.utils.html import format_html
from .models import FAQ


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
