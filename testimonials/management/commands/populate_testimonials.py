from django.core.management.base import BaseCommand
from testimonials.models import Testimonial


class Command(BaseCommand):
    help = 'Populate testimonials with sample data'

    def handle(self, *args, **kwargs):
        # Clear existing testimonials
        Testimonial.objects.all().delete()
        
        testimonials_data = [
            {
                'title': 'Brilliant Service',
                'name': 'Logan Holt',
                'role': 'BUYER',
                'text': 'Working with this team was an absolute pleasure. They helped us find our dream home within our budget and made the entire process smooth and stress-free. Their knowledge of the local market was invaluable.',
                'rating': 5,
                'order': 1,
            },
            {
                'title': 'The Best Realtor',
                'name': 'Mollie Hope',
                'role': 'BUYER',
                'text': 'Professional, knowledgeable, and always available to answer our questions. They went above and beyond to ensure we found the perfect property. Highly recommend their services to anyone looking to buy.',
                'rating': 5,
                'order': 2,
            },
            {
                'title': 'Highly Recommended',
                'name': 'James Wilson',
                'role': 'SELLER',
                'text': 'Sold our house in record time at a great price. The marketing strategy was excellent and the communication throughout the process was outstanding. Could not have asked for better service.',
                'rating': 5,
                'order': 3,
            },
            {
                'title': 'Professional Team',
                'name': 'Sarah Jenkins',
                'role': 'BUYER',
                'text': 'From start to finish, the experience was exceptional. They listened to our needs and showed us properties that matched exactly what we were looking for. Very patient and professional throughout.',
                'rating': 5,
                'order': 4,
            },
            {
                'title': 'Great Experience',
                'name': 'Emily Davis',
                'role': 'SELLER',
                'text': 'Made selling our home easy and stress-free. Their expertise in pricing and negotiation resulted in a quick sale at an excellent price. Would definitely work with them again in the future.',
                'rating': 5,
                'order': 5,
            },
            {
                'title': 'Very Helpful',
                'name': 'Michael Brown',
                'role': 'BUYER',
                'text': 'Extremely helpful and responsive throughout our home buying journey. They took the time to understand our needs and found us the perfect home. Their guidance was invaluable for first-time buyers like us.',
                'rating': 5,
                'order': 6,
            },
        ]
        
        for data in testimonials_data:
            Testimonial.objects.create(**data)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(testimonials_data)} testimonials'
            )
        )
