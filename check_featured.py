import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtor_pal.settings')
django.setup()

from testimonials.models import Testimonial

featured = Testimonial.objects.filter(is_featured=True)
print(f'Total featured testimonials: {featured.count()}')
print('\nFeatured testimonials:')
for t in featured:
    print(f'- ID: {t.id}')
    print(f'  Name: {t.name}')
    print(f'  Title: {t.title}')
    print(f'  Role: {t.role}')
    print(f'  Image: {t.image.url if t.image else "No image"}')
    print(f'  Video URL: {t.video_url or "None"}')
    print(f'  Approved: {t.is_approved}')
    print()
