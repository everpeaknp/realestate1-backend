"""
Management command to populate Properties Hero Settings
Run with: python manage.py populate_properties_hero
"""

from django.core.management.base import BaseCommand
from properties.models import PropertiesHeroSettings


class Command(BaseCommand):
    help = 'Populate Properties Hero Settings with default data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🏠 Populating Properties Hero Settings...\n')
        
        # Create or update the singleton settings
        settings, created = PropertiesHeroSettings.objects.get_or_create(pk=1)
        
        settings.title = "Properties"
        settings.subtitle = "Find your dream homes with me."
        settings.background_image_url = "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=1920"
        settings.is_active = True
        
        settings.save()
        
        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f'\n✅ {action} Properties Hero Settings:'))
        self.stdout.write(f'   Title: {settings.title}')
        self.stdout.write(f'   Subtitle: {settings.subtitle}')
        self.stdout.write(f'   Background URL: {settings.background_image_url[:60]}...')
        self.stdout.write('\n💡 You can now customize these settings in the Django admin:')
        self.stdout.write('   http://localhost:8000/admin/properties/propertiesherosettings/')
