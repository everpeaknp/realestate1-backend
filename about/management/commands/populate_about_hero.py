"""
Management command to populate About Hero Settings
Run with: python manage.py populate_about_hero
"""

from django.core.management.base import BaseCommand
from about.models import AboutHeroSettings


class Command(BaseCommand):
    help = 'Populate About Hero Settings with default data'

    def handle(self, *args, **kwargs):
        self.stdout.write('👤 Populating About Hero Settings...\n')
        
        # Create or update the singleton settings
        settings, created = AboutHeroSettings.objects.get_or_create(pk=1)
        
        settings.title = "Hello, I'm Justin Nelson"
        settings.subtitle = "Boston's most acceptable realtor you can trust."
        settings.background_image_url = "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&q=80&w=1920"
        settings.is_active = True
        
        settings.save()
        
        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f'\n✅ {action} About Hero Settings:'))
        self.stdout.write(f'   Title: {settings.title}')
        self.stdout.write(f'   Subtitle: {settings.subtitle}')
        self.stdout.write(f'   Background URL: {settings.background_image_url[:60]}...')
        self.stdout.write('\n💡 You can now customize these settings in the Django admin:')
        self.stdout.write('   http://localhost:8000/admin/about/aboutherosettings/')
