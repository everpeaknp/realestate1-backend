from django.contrib import admin
from .models import (
    HeroSettings, HeroCard, HowItWorksStep, Neighborhood,
    Benefit, BenefitGalleryImage, BenefitsSection,
    ContactSectionSettings, InstagramImage, PersonSectionSettings, StatItem
)


@admin.register(HeroSettings)
class HeroSettingsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'updated_at']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle')
        }),
        ('Background', {
            'fields': ('background_image',)
        }),
        ('Primary Button', {
            'fields': ('primary_button_text', 'primary_button_link')
        }),
        ('Secondary Button', {
            'fields': ('secondary_button_text', 'secondary_button_link')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def has_add_permission(self, request):
        return not HeroSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class HeroCardInline(admin.TabularInline):
    model = HeroCard
    extra = 0
    fields = ['title', 'description', 'icon_name', 'link', 'order', 'is_active']
    ordering = ['order', 'id']


@admin.register(HeroCard)
class HeroCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon_name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    ordering = ['order', 'id']


@admin.register(HowItWorksStep)
class HowItWorksStepAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'icon_name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    ordering = ['order', 'number']


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['order', 'id']


class BenefitInline(admin.TabularInline):
    model = Benefit
    extra = 1
    fields = ['text', 'order', 'is_active']
    ordering = ['order', 'id']


class BenefitGalleryImageInline(admin.TabularInline):
    model = BenefitGalleryImage
    extra = 1
    fields = ['image', 'alt_text', 'order', 'is_active']
    ordering = ['order', 'id']


@admin.register(BenefitsSection)
class BenefitsSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'phone', 'email', 'is_active', 'updated_at']
    fieldsets = (
        ('Section Content', {
            'fields': ('title', 'description')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    inlines = [BenefitInline, BenefitGalleryImageInline]

    def has_add_permission(self, request):
        return not BenefitsSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactSectionSettings)
class ContactSectionSettingsAdmin(admin.ModelAdmin):
    list_display = ['card_title', 'is_active', 'updated_at']
    fieldsets = (
        ('Image', {
            'fields': ('person_image',)
        }),
        ('Card Content', {
            'fields': ('card_title', 'card_subtitle', 'card_description')
        }),
        ('Button', {
            'fields': ('button_text', 'button_link')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def has_add_permission(self, request):
        return not ContactSectionSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(InstagramImage)
class InstagramImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'link', 'alt_text', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['alt_text', 'link']
    ordering = ['order', 'id']


@admin.register(PersonSectionSettings)
class PersonSectionSettingsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'updated_at']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'description')
        }),
        ('Image', {
            'fields': ('person_image',)
        }),
        ('Button', {
            'fields': ('button_text', 'button_link')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def has_add_permission(self, request):
        return not PersonSectionSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StatItem)
class StatItemAdmin(admin.ModelAdmin):
    list_display = ['label', 'icon_name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['label', 'description']
    ordering = ['order', 'id']
