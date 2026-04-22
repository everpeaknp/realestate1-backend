from django.contrib import admin
from django.utils.html import format_html
from .models import Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    """Inline admin for property images"""
    model = PropertyImage
    extra = 1
    fields = ('image', 'caption', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 4px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Enhanced admin for Property model with Jazzmin optimization"""
    list_display = (
        'title', 'property_type_badge', 'status_badge', 'price_display', 
        'location_display', 'beds', 'baths', 'sqft', 
        'is_featured_icon', 'created_at'
    )
    list_filter = ('property_type', 'status', 'is_featured', 'city', 'state', 'created_at')
    search_fields = ('title', 'address', 'city', 'state', 'zip_code', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'main_image_preview')
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'property_type', 'status', 'is_featured')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'zip_code', 'latitude', 'longitude')
        }),
        ('Pricing & Features', {
            'fields': ('price', 'beds', 'baths', 'garage', 'sqft', 'year_built', 'lot_size')
        }),
        ('Images', {
            'fields': ('main_image', 'main_image_preview', 'floor_plan')
        }),
        ('Additional Information', {
            'fields': ('amenities', 'agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PropertyImageInline]
    
    def property_type_badge(self, obj):
        colors = {
            'FOR_SALE': '#28a745',
            'FOR_RENT': '#007bff'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.property_type, '#6c757d'),
            obj.get_property_type_display()
        )
    property_type_badge.short_description = 'Type'
    property_type_badge.admin_order_field = 'property_type'
    
    def status_badge(self, obj):
        colors = {
            'AVAILABLE': '#28a745',
            'PENDING': '#ffc107',
            'SOLD': '#dc3545',
            'RENTED': '#17a2b8'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def price_display(self, obj):
        formatted_price = f'{obj.price:,.0f}'
        return format_html('<strong>${}</strong>', formatted_price)
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'
    
    def is_featured_icon(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: #ffc107; font-size: 18px;">★</span>')
        return format_html('<span style="color: #ddd; font-size: 18px;">☆</span>')
    is_featured_icon.short_description = 'Featured'
    is_featured_icon.admin_order_field = 'is_featured'
    
    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />', obj.main_image.url)
        return format_html('<p style="color: #999;">No image uploaded</p>')
    main_image_preview.short_description = 'Main Image Preview'
    
    actions = ['mark_as_featured', 'remove_featured', 'mark_as_available', 'mark_as_sold', 'mark_as_rented']
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} properties marked as featured.', 'success')
    mark_as_featured.short_description = '⭐ Mark selected as featured'
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} properties removed from featured.', 'success')
    remove_featured.short_description = '☆ Remove from featured'
    
    def mark_as_available(self, request, queryset):
        updated = queryset.update(status='AVAILABLE')
        self.message_user(request, f'{updated} properties marked as available.', 'success')
    mark_as_available.short_description = '✓ Mark as available'
    
    def mark_as_sold(self, request, queryset):
        updated = queryset.update(status='SOLD')
        self.message_user(request, f'{updated} properties marked as sold.', 'success')
    mark_as_sold.short_description = '✓ Mark as sold'
    
    def mark_as_rented(self, request, queryset):
        updated = queryset.update(status='RENTED')
        self.message_user(request, f'{updated} properties marked as rented.', 'success')
    mark_as_rented.short_description = '✓ Mark as rented'


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """Admin for property images"""
    list_display = ('property', 'caption', 'order', 'image_preview')
    list_filter = ('property',)
    search_fields = ('property__title', 'caption')
    list_editable = ('order',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 4px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'
