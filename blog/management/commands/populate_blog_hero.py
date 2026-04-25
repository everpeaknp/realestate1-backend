"""
Management command to populate blog hero settings with default data
Usage: python manage.py populate_blog_hero
"""

from django.core.management.base import BaseCommand
from blog.models import BlogHeroSettings


class Command(BaseCommand):
    help = 'Populate blog hero settings with default data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Populating blog hero settings...'))
        
        # Get or create the singleton settings instance
        settings, created = BlogHeroSettings.objects.get_or_create(
            pk=1,
            defaults={
                'title': 'Blog',
                'subtitle': 'Insights, tips, and stories from the world of real estate',
                'background_image_url': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&q=80&w=1920',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully created blog hero settings:\n'
                    f'  - Title: {settings.title}\n'
                    f'  - Subtitle: {settings.subtitle}\n'
                    f'  - Background URL: {settings.background_image_url}\n'
                    f'  - Active: {settings.is_active}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Blog hero settings already exist:\n'
                    f'  - Title: {settings.title}\n'
                    f'  - Subtitle: {settings.subtitle}\n'
                    f'  - Background URL: {settings.background_image_url}\n'
                    f'  - Active: {settings.is_active}\n'
                    f'\nNo changes made. Update via Django admin if needed.'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Blog hero settings are ready!\n'
                f'  Admin URL: http://localhost:8000/admin/blog/blogherosettings/\n'
                f'  API URL: http://localhost:8000/api/blog/hero-settings/'
            )
        )
