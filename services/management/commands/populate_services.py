import os
import requests
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files import File
from services.models import Service, ServiceFeature


class Command(BaseCommand):
    help = 'Populate services with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating services...')
        
        # Clear existing services
        Service.objects.all().delete()
        
        services_data = [
            {
                'title': 'Buy Property',
                'slug': 'buy-property',
                'description': 'Etiam porta sem malesuada magna mollis euismod. Cras justo odio, dapibus ac facilisis in, egestas eget quam. Sed posuere consectetur est at lobortis. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Donec ullamcorper nulla non metus auctor fringilla.',
                'layout': 'IMAGE_LEFT',
                'phone': '+1 (321) 456 7890',
                'email': 'hello@example.com',
                'button_text': 'Contact Me',
                'order': 1,
                'image_url': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=600',
                'features': [
                    'Ornare sem lacinia quam venenatis vestibulum.',
                    'Morbi leo risus porta vestibulum at eros.',
                    'Donec id elit non mi porta gravida at eget metus.',
                    'Nulla vitae elit libero, a pharetra augue.'
                ]
            },
            {
                'title': 'Sell Property',
                'slug': 'sell-property',
                'description': 'Etiam porta sem malesuada magna mollis euismod. Cras justo odio, dapibus ac facilisis in, egestas eget quam. Sed posuere consectetur est at lobortis. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Donec ullamcorper nulla non metus auctor fringilla.',
                'layout': 'IMAGE_RIGHT',
                'phone': '+1 (321) 456 7890',
                'email': 'hello@example.com',
                'button_text': 'Contact Me',
                'order': 2,
                'image_url': 'https://images.unsplash.com/photo-1582407947304-fd86f028f716?auto=format&fit=crop&q=80&w=600',
                'features': [
                    'Ornare sem lacinia quam venenatis vestibulum.',
                    'Morbi leo risus porta vestibulum at eros.',
                    'Donec id elit non mi porta gravida at eget metus.',
                    'Nulla vitae elit libero, a pharetra augue.'
                ]
            },
            {
                'title': 'Rent Property',
                'slug': 'rent-property',
                'description': 'Etiam porta sem malesuada magna mollis euismod. Cras justo odio, dapibus ac facilisis in, egestas eget quam. Sed posuere consectetur est at lobortis. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Donec ullamcorper nulla non metus auctor fringilla.',
                'layout': 'IMAGE_LEFT',
                'phone': '+1 (321) 456 7890',
                'email': 'hello@example.com',
                'button_text': 'Contact Me',
                'order': 3,
                'image_url': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=600',
                'features': [
                    'Ornare sem lacinia quam venenatis vestibulum.',
                    'Morbi leo risus porta vestibulum at eros.',
                    'Donec id elit non mi porta gravida at eget metus.',
                    'Nulla vitae elit libero, a pharetra augue.'
                ]
            },
            {
                'title': 'Home Loan',
                'slug': 'home-loan',
                'description': 'Etiam porta sem malesuada magna mollis euismod. Cras justo odio, dapibus ac facilisis in, egestas eget quam. Sed posuere consectetur est at lobortis. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Donec ullamcorper nulla non metus auctor fringilla.',
                'layout': 'IMAGE_RIGHT',
                'phone': '+1 (321) 456 7890',
                'email': 'hello@example.com',
                'button_text': 'Contact Me',
                'order': 4,
                'image_url': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=600',
                'features': [
                    'Ornare sem lacinia quam venenatis vestibulum.',
                    'Morbi leo risus porta vestibulum at eros.',
                    'Donec id elit non mi porta gravida at eget metus.',
                    'Nulla vitae elit libero, a pharetra augue.'
                ]
            }
        ]
        
        for service_data in services_data:
            self.stdout.write(f'Creating service: {service_data["title"]}')
            
            # Download image
            image_url = service_data.pop('image_url')
            features_data = service_data.pop('features')
            
            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                
                # Create service
                service = Service.objects.create(**service_data)
                
                # Save image
                image_name = f'{service.slug}.jpg'
                service.image.save(
                    image_name,
                    File(BytesIO(response.content)),
                    save=True
                )
                
                # Create features
                for idx, feature_text in enumerate(features_data):
                    ServiceFeature.objects.create(
                        service=service,
                        text=feature_text,
                        order=idx
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created service: {service.title}')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creating {service_data["title"]}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully created {Service.objects.count()} services')
        )
