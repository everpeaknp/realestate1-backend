from django.core.management.base import BaseCommand
from services.models import Service, ServicesHeroSettings


class Command(BaseCommand):
    help = 'Fix service images - move URLs from image field to image_url field'

    def handle(self, *args, **kwargs):
        self.stdout.write('Fixing service images...')
        
        # Fix Service images
        services = Service.objects.all()
        for service in services:
            # If image field contains a URL (starts with http), move it to image_url
            if service.image and str(service.image).startswith('http'):
                url = str(service.image)
                service.image_url = url
                service.image = None  # Clear the image field
                service.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Fixed {service.title}: moved URL to image_url field'))
            elif service.image and str(service.image).startswith('/media/http'):
                # Fix malformed URLs that got saved with /media/ prefix
                url = str(service.image).replace('/media/https%3A/', 'https://').replace('%3A', ':').replace('%3D', '=').replace('%26', '&').replace('%3F', '?')
                service.image_url = url
                service.image = None
                service.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Fixed {service.title}: cleaned malformed URL'))
        
        # Fix ServicesHeroSettings background
        try:
            hero = ServicesHeroSettings.objects.first()
            if hero and hero.background_image and str(hero.background_image).startswith('http'):
                url = str(hero.background_image)
                hero.background_url = url
                hero.background_image = None
                hero.save()
                self.stdout.write(self.style.SUCCESS('✓ Fixed hero background: moved URL to background_url field'))
        except ServicesHeroSettings.DoesNotExist:
            pass
        
        self.stdout.write(self.style.SUCCESS('\n✅ Service images fixed!'))
