import os
import requests
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files import File
from about.models import Goal, ServicesProvide


class Command(BaseCommand):
    help = 'Populate about section with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating about section...')
        
        # Clear existing data
        Goal.objects.all().delete()
        ServicesProvide.objects.all().delete()
        
        # Create Goals
        goals_data = [
            {
                'title': 'Full Service Agent',
                'description': "I'm honored that client referrals built my growing client family exclusively. My tried-and-true techniques give my clients a competitive advantage in this market environment.",
                'order': 1,
            },
            {
                'title': 'My Approach',
                'description': 'I intend not just to make a good impact on ourselves and our families but also to inspire, encourage, and bring about permanent change in everyone we meet.',
                'order': 2,
            },
            {
                'title': 'My Values',
                'description': 'My work ethic and the success of my business are driven by this guiding principle, which motivates me to maintain long-lasting connections with clients.',
                'order': 3,
            }
        ]
        
        for goal_data in goals_data:
            goal = Goal.objects.create(**goal_data)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created goal: {goal.title}')
            )
        
        # Create Services Provide Section
        self.stdout.write('Creating Services Provide section...')
        
        image_url = 'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&q=80&w=1920'
        
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            services_provide = ServicesProvide.objects.create(
                subtitle='Services I Provide',
                title='Appreciated for consistently outperforming client expectations and providing exceptional results.',
                is_active=True
            )
            
            # Save image
            services_provide.background_image.save(
                'services-provide-bg.jpg',
                File(BytesIO(response.content)),
                save=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created Services Provide section')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating Services Provide section: {str(e)}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully populated about section')
        )
