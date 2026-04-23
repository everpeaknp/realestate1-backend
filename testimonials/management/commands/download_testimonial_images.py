from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from testimonials.models import Testimonial
import requests


class Command(BaseCommand):
    help = 'Download sample images for testimonials'

    def handle(self, *args, **kwargs):
        image_urls = [
            'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&q=80&w=300',
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&q=80&w=300',
            'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&q=80&w=300',
            'https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&q=80&w=300',
            'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=300',
            'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=300',
        ]
        
        testimonials = Testimonial.objects.all().order_by('order')
        
        for idx, testimonial in enumerate(testimonials):
            if idx < len(image_urls):
                try:
                    response = requests.get(image_urls[idx], timeout=10)
                    if response.status_code == 200:
                        filename = f'{testimonial.name.lower().replace(" ", "_")}.jpg'
                        testimonial.image.save(
                            filename,
                            ContentFile(response.content),
                            save=True
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Downloaded image for {testimonial.name}'
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Failed to download image for {testimonial.name}: {str(e)}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS('Finished downloading testimonial images')
        )
