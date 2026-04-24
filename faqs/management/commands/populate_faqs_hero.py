from django.core.management.base import BaseCommand
from faqs.models import FAQsHeroSettings


class Command(BaseCommand):
    help = 'Populate FAQs hero settings with default data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating FAQs hero settings...')
        
        # Create or update hero settings
        hero, created = FAQsHeroSettings.objects.get_or_create(
            pk=1,
            defaults={
                'title': 'Common Queries',
                'subtitle': 'My only purpose is to deliver successful results.',
                'background_image_url': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&q=80&w=1920',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created FAQs hero settings'))
        else:
            self.stdout.write(self.style.WARNING('→ FAQs hero settings already exist'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ FAQs hero population complete!'))
