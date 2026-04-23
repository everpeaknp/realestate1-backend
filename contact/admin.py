from django.contrib import admin
from .models import ContactCard, ContactFormSettings


@admin.register(ContactCard)
class ContactCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'value', 'icon', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'icon']
    search_fields = ['title', 'value']
    ordering = ['order', 'id']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('title', 'value', 'icon')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    actions = ['activate_cards', 'deactivate_cards']
    
    def activate_cards(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} contact card(s) activated.')
    activate_cards.short_description = 'Activate selected contact cards'
    
    def deactivate_cards(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} contact card(s) deactivated.')
    deactivate_cards.short_description = 'Deactivate selected contact cards'


@admin.register(ContactFormSettings)
class ContactFormSettingsAdmin(admin.ModelAdmin):
    list_display = ['agent_name', 'agent_title', 'is_active']
    
    fieldsets = (
        ('Introduction', {
            'fields': ('intro_text',)
        }),
        ('Agent Information', {
            'fields': ('agent_name', 'agent_title', 'agent_image')
        }),
        ('Social Media Links', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance (singleton pattern)
        return not ContactFormSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False
