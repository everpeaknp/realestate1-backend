from django.contrib import admin
from django.utils.html import format_html
from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Enhanced admin for Testimonial model with Jazzmin optimization"""
    list_display = (
        'client_name', 'rating_display', 'property_type', 
        'is_approved_icon', 'is_featured_icon', 'has_video_icon', 'created_at'
    )
    list_filter = ('rating', 'is_approved', 'is_featured', 'created_at')
    search_fields = ('client_name', 'content', 'property_type')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('Client Information', {
            'fields': ('client_name', 'client_avatar')
        }),
        ('Testimonial', {
            'fields': ('rating', 'content', 'property_type')
        }),
        ('Media', {
            'fields': ('video_url',)
        }),
        ('Status', {
            'fields': ('is_approved', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107; font-size: 16px; letter-spacing: 2px;">{}</span>', stars)
    rating_display.short_description = 'Rating'
    rating_display.admin_order_field = 'rating'
    
    def is_approved_icon(self, obj):
        if obj.is_approved:
            return format_html('<span style="color: #28a745; font-size: 18px;">✓</span>')
        return format_html('<span style="color: #dc3545; font-size: 18px;">✗</span>')
    is_approved_icon.short_description = 'Approved'
    is_approved_icon.admin_order_field = 'is_approved'
    
    def is_featured_icon(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: #ffc107; font-size: 18px;">★</span>')
        return format_html('<span style="color: #ddd; font-size: 18px;">☆</span>')
    is_featured_icon.short_description = 'Featured'
    is_featured_icon.admin_order_field = 'is_featured'
    
    def has_video_icon(self, obj):
        if obj.video_url:
            return format_html('<span style="color: #dc3545; font-size: 16px;">&#9654;</span>')
        return format_html('<span style="color: #ddd; font-size: 16px;">-</span>')
    has_video_icon.short_description = 'Video'
    
    actions = ['approve_testimonials', 'unapprove_testimonials', 'mark_as_featured', 'remove_featured']
    
    def approve_testimonials(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} testimonials approved.', 'success')
    approve_testimonials.short_description = '✓ Approve selected testimonials'
    
    def unapprove_testimonials(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} testimonials unapproved.', 'warning')
    unapprove_testimonials.short_description = '✗ Unapprove selected testimonials'
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} testimonials marked as featured.', 'success')
    mark_as_featured.short_description = '⭐ Mark as featured'
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} testimonials removed from featured.', 'success')
    remove_featured.short_description = '☆ Remove from featured'
