from django.core.management.base import BaseCommand
from projects.models import ProjectsHeroSettings


class Command(BaseCommand):
    help = 'Populate projects hero settings with default data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating projects hero settings...')
        
        # Create or update hero settings
        hero, created = ProjectsHeroSettings.objects.get_or_create(
            pk=1,
            defaults={
                'title': 'Projects',
                'subtitle': 'Your exquisite partners in finding home solutions',
                'background_image_url': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&q=80&w=1920',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created projects hero settings'))
        else:
            self.stdout.write(self.style.WARNING('→ Projects hero settings already exist'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Projects hero population complete!'))
