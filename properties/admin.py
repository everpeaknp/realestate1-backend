from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import reverse
from .models import (
    Property,
    PropertyImage,
    PropertyFeature,
    PropertiesHeroSettings,
    FilterOption,
    ExternalPropertyFeed,
)


from django.forms import BaseInlineFormSet


class FilterOptionFormSet(BaseInlineFormSet):
    def save_new(self, form, commit=True):
        obj = super().save_new(form, commit=False)
        obj.category = self.category_filter
        if commit:
            obj.save()
        return obj


class BaseFilterOptionInline(admin.TabularInline):
    """Base class for filtered inlines"""
    model = FilterOption
    formset = FilterOptionFormSet
    extra = 1
    fields = ('label', 'value', 'order')
    sortable_field_name = 'order'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(self, 'category_filter'):
            return qs.filter(category=self.category_filter)
        return qs

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.category_filter = self.category_filter
        return formset


class PropertyTypeInline(BaseFilterOptionInline):
    verbose_name = "Property Type"
    verbose_name_plural = "Property Types (e.g. House, Apartment)"
    category_filter = 'PROPERTY_TYPE'


class MinPriceInline(BaseFilterOptionInline):
    verbose_name = "Min Price Option"
    verbose_name_plural = "Min Price Dropdown Options"
    category_filter = 'MIN_PRICE'


class MaxPriceInline(BaseFilterOptionInline):
    verbose_name = "Max Price Option"
    verbose_name_plural = "Max Price Dropdown Options"
    category_filter = 'MAX_PRICE'


class BedroomInline(BaseFilterOptionInline):
    verbose_name = "Bedroom Option"
    verbose_name_plural = "Bedroom Dropdown Options"
    category_filter = 'BEDROOMS'


class StatusInline(BaseFilterOptionInline):
    verbose_name = "Listing Status"
    verbose_name_plural = "Listing Status Options (e.g. For Sale, Sold)"
    category_filter = 'STATUS'


@admin.register(PropertiesHeroSettings)
class PropertiesHeroSettingsAdmin(admin.ModelAdmin):
    """Admin for Properties Hero Settings with organized filter sections"""
    list_display = ['title', 'subtitle', 'is_active']
    inlines = [PropertyTypeInline, MinPriceInline, MaxPriceInline, BedroomInline, StatusInline]
    
    fieldsets = (
        ('Hero Content', {
            'fields': ('title', 'subtitle')
        }),
        ('Background Image', {
            'fields': ('background_image', 'background_image_preview', 'background_image_url'),
            'description': 'Upload a custom background image or use the URL fallback'
        }),
        ('Filter Display Settings', {
            'fields': ('show_filters', 'filter_title'),
            'description': 'Control the visibility and label of the filter bar'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ('background_image_preview',)
    
    def background_image_preview(self, obj):
        if obj.background_image:
            return format_html(
                '<img src="{}" style="max-width: 600px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.background_image.url
            )
        elif obj.background_image_url:
            return format_html(
                '<img src="{}" style="max-width: 600px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" /><br><small style="color: #666;">Using fallback URL</small>',
                obj.background_image_url
            )
        return format_html('<p style="color: #999;">{}</p>', 'No image')
    background_image_preview.short_description = 'Preview'
    
    def changelist_view(self, request, extra_context=None):
        """Redirect to the single instance edit page for singleton model"""
        obj = PropertiesHeroSettings.objects.first()
        if obj:
            url = reverse('admin:properties_propertiesherosettings_change', args=[obj.pk])
            return redirect(url)
        return super().changelist_view(request, extra_context=extra_context)
    
    def has_add_permission(self, request):
        # Only allow one instance (singleton pattern)
        return not PropertiesHeroSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False


class PropertyImageInline(admin.TabularInline):
    """Inline admin for property gallery images"""
    model = PropertyImage
    extra = 3
    fields = ('image', 'caption', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    verbose_name = 'Gallery Image'
    verbose_name_plural = 'Gallery Images'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 120px; border-radius: 4px; object-fit: cover;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">{}</span>', 'No image')
    image_preview.short_description = 'Preview'


class PropertyFeatureInline(admin.TabularInline):
    """Inline admin for property features"""
    model = PropertyFeature
    extra = 5
    fields = ('category', 'name', 'icon', 'order')
    verbose_name = 'Feature'
    verbose_name_plural = 'Features & Amenities'


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
    readonly_fields = ('created_at', 'updated_at', 'main_image_preview', 'floor_plan_preview')
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
            'fields': ('main_image', 'main_image_preview', 'floor_plan', 'floor_plan_preview'),
            'description': 'Upload main property image and floor plan. Gallery images can be added below.'
        }),
        ('Additional Information', {
            'fields': ('amenities', 'agent'),
            'classes': ('collapse',),
            'description': 'Legacy amenities field (comma-separated). Use Features section below for structured features.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PropertyImageInline, PropertyFeatureInline]
    
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
    
    def location_display(self, obj):
        return f"{obj.city}, {obj.state}"
    location_display.short_description = 'Location'
    location_display.admin_order_field = 'city'
    
    def is_featured_icon(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: #ffc107; font-size: 18px;">{}</span>', '★')
        return format_html('<span style="color: #ddd; font-size: 18px;">{}</span>', '☆')
    is_featured_icon.short_description = 'Featured'
    is_featured_icon.admin_order_field = 'is_featured'
    
    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.main_image.url
            )
        return format_html('<p style="color: #999;">{}</p>', 'No image uploaded')
    main_image_preview.short_description = 'Main Image Preview'
    
    def floor_plan_preview(self, obj):
        if obj.floor_plan:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.floor_plan.url
            )
        return format_html('<p style="color: #999;">{}</p>', 'No floor plan uploaded')
    floor_plan_preview.short_description = 'Floor Plan Preview'
    
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
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 4px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    """Admin for property features"""
    list_display = ('property', 'category', 'name', 'icon', 'order')
    list_filter = ('category', 'property')
    search_fields = ('property__title', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('property', 'category', 'name', 'icon', 'order')
        }),
    )


@admin.register(ExternalPropertyFeed)
class ExternalPropertyFeedAdmin(admin.ModelAdmin):
    list_display = (
        'external_id',
        'status',
        'property_type',
        'formatted_address',
        'price',
        'is_active',
        'updated_at',
    )
    list_filter = ('status', 'property_type', 'listing_type', 'is_active', 'updated_at')
    search_fields = (
        'external_id',
        'formatted_address',
        'headline',
        'suburb',
        'agent_name',
        'agent_email',
    )
    readonly_fields = ('created_at', 'updated_at', 'last_seen_at')
    list_per_page = 50
