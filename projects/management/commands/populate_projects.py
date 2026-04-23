from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from projects.models import Project, ProjectImage
import requests
from datetime import date, timedelta
import random
from io import BytesIO


class Command(BaseCommand):
    help = 'Populate projects with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating projects...')
        
        # Clear existing projects
        Project.objects.all().delete()
        
        projects_data = [
            {
                'title': 'Modern Villa Exterior',
                'description': 'A stunning modern villa featuring clean lines, large windows, and contemporary architecture. This project showcases our expertise in luxury residential design.',
                'location': 'Beverly Hills, CA',
                'category': 'LUXURY',
                'is_featured': True,
                'order': 1,
            },
            {
                'title': 'Luxury Pool Area',
                'description': 'An elegant outdoor living space with infinity pool, modern landscaping, and premium finishes. Perfect blend of functionality and aesthetics.',
                'location': 'Malibu, CA',
                'category': 'LUXURY',
                'is_featured': True,
                'order': 2,
            },
            {
                'title': 'Contemporary Living Room',
                'description': 'Spacious living area with floor-to-ceiling windows, modern furniture, and sophisticated interior design.',
                'location': 'Manhattan, NY',
                'category': 'MODERN',
                'is_featured': True,
                'order': 3,
            },
            {
                'title': 'Elegant Kitchen Design',
                'description': 'State-of-the-art kitchen with premium appliances, custom cabinetry, and marble countertops.',
                'location': 'San Francisco, CA',
                'category': 'RESIDENTIAL',
                'is_featured': False,
                'order': 4,
            },
            {
                'title': 'Minimalist Balcony',
                'description': 'Clean and modern balcony design with stunning city views and contemporary outdoor furniture.',
                'location': 'Chicago, IL',
                'category': 'MODERN',
                'is_featured': False,
                'order': 5,
            },
        ]

        
        # Sample Unsplash image IDs for real estate
        image_urls = [
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800',
            'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800',
            'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=800',
            'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800',
            'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800',
            'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800',
            'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=800',
            'https://images.unsplash.com/photo-1600573472591-ee6b68d14c68?w=800',
            'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800',
            'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800',
        ]
        
        for idx, project_data in enumerate(projects_data):
            # Create project
            completion_date = date.today() - timedelta(days=random.randint(30, 365))
            project = Project.objects.create(
                **project_data,
                completion_date=completion_date
            )
            
            self.stdout.write(f'Created project: {project.title}')
            
            # Add 2-4 images per project
            num_images = random.randint(2, 4)
            for i in range(num_images):
                image_url = random.choice(image_urls)
                
                try:
                    # Download image
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        # Create image file
                        image_content = ContentFile(response.content)
                        filename = f'project_{project.id}_image_{i}.jpg'
                        
                        project_image = ProjectImage.objects.create(
                            project=project,
                            title=f'{project.title} - View {i+1}',
                            order=i
                        )
                        project_image.image.save(filename, image_content, save=True)
                        self.stdout.write(f'  Added image {i+1}')
                    else:
                        self.stdout.write(self.style.WARNING(f'  Failed to download image {i+1}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error downloading image {i+1}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(projects_data)} projects'))
