from django.core.management.base import BaseCommand
from testimonials.models import TestimonialsHeroSettings


class Command(BaseCommand):
    help = 'Populate testimonials hero settings with default data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating testimonials hero settings...')
        
        # Create or update hero settings
        hero, created = TestimonialsHeroSettings.objects.get_or_create(
            pk=1,
            defaults={
                'title': 'Testimonials',
                'subtitle': 'Helping you get more for your real estate.',
                'background_image_url': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&q=80&w=1920',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created testimonials hero settings'))
        else:
            self.stdout.write(self.style.WARNING('→ Testimonials hero settings already exist'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Testimonials hero population complete!'))
