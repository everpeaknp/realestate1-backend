"""
Management command to populate contact hero settings with default data
Usage: python manage.py populate_contact_hero
"""

from django.core.management.base import BaseCommand
from contact.models import ContactHeroSettings


class Command(BaseCommand):
    help = 'Populate contact hero settings with default data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Populating contact hero settings...'))
        
        # Get or create the singleton settings instance
        settings, created = ContactHeroSettings.objects.get_or_create(
            pk=1,
            defaults={
                'title': 'Contact Me',
                'subtitle': 'Get in touch and let me help you find your dream property',
                'background_image_url': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&q=80&w=1920',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully created contact hero settings:\n'
                    f'  - Title: {settings.title}\n'
                    f'  - Subtitle: {settings.subtitle}\n'
                    f'  - Background URL: {settings.background_image_url}\n'
                    f'  - Active: {settings.is_active}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Contact hero settings already exist:\n'
                    f'  - Title: {settings.title}\n'
                    f'  - Subtitle: {settings.subtitle}\n'
                    f'  - Background URL: {settings.background_image_url}\n'
                    f'  - Active: {settings.is_active}\n'
                    f'\nNo changes made. Update via Django admin if needed.'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Contact hero settings are ready!\n'
                f'  Admin URL: http://localhost:8000/admin/contact/contactherosettings/\n'
                f'  API URL: http://localhost:8000/api/contact/hero-settings/'
            )
        )
