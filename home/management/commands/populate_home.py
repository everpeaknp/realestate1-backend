from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from home.models import (
    HeroSettings, HeroCard, HowItWorksStep, Neighborhood,
    Benefit, BenefitGalleryImage, BenefitsSection,
    ContactSectionSettings, InstagramImage, PersonSectionSettings, StatItem
)
import requests
from io import BytesIO


class Command(BaseCommand):
    help = 'Populate home page with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating home page data...')

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        HeroCard.objects.all().delete()
        HowItWorksStep.objects.all().delete()
        Neighborhood.objects.all().delete()
        Benefit.objects.all().delete()
        BenefitGalleryImage.objects.all().delete()
        InstagramImage.objects.all().delete()
        StatItem.objects.all().delete()

        # Create Hero Settings
        self.create_hero_settings()

        # Create Hero Cards
        self.create_hero_cards()

        # Create How It Works Steps
        self.create_how_it_works()

        # Create Neighborhoods
        self.create_neighborhoods()

        # Create Benefits
        self.create_benefits()

        # Create Benefits Contact Info
        self.create_benefits_contact()

        # Create Contact Section Settings
        self.create_contact_section()

        # Create Instagram Images
        self.create_instagram_images()

        # Create Person Section Settings
        self.create_person_section()

        # Create Stats
        self.create_stats()

        self.stdout.write(self.style.SUCCESS('Successfully populated home page data!'))

    def download_image(self, url):
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return ContentFile(response.content)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Failed to download image: {e}'))
        return None

    def create_hero_settings(self):
        """Create hero settings"""
        self.stdout.write('Creating hero settings...')
        hero, created = HeroSettings.objects.get_or_create(
            defaults={
                'title': 'Find Your Dream Home',
                'subtitle': 'Discover the perfect property that matches your lifestyle and budget. Browse through our extensive collection of homes, apartments, and commercial spaces.',
                'primary_button_text': 'View Properties',
                'primary_button_link': '/properties',
                'secondary_button_text': 'Contact Me',
                'secondary_button_link': '/contact',
                'is_active': True
            }
        )
        
        # Download and set background image
        if created:
            image_url = 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1920&h=1080&fit=crop'
            image_content = self.download_image(image_url)
            if image_content:
                hero.background_image.save('hero-bg.jpg', image_content, save=True)
        
        self.stdout.write(self.style.SUCCESS('✓ Hero settings created'))

    def create_hero_cards(self):
        """Create hero cards"""
        self.stdout.write('Creating hero cards...')
        cards = [
            {
                'title': 'Buy a Property',
                'description': 'Find your perfect home from our extensive listings',
                'icon_name': 'home',
                'link': '/services#buy',
                'order': 1
            },
            {
                'title': 'Sell a Property',
                'description': 'Get the best value for your property',
                'icon_name': 'key',
                'link': '/services#sell',
                'order': 2
            },
            {
                'title': 'Rent a Property',
                'description': 'Discover rental properties that suit your needs',
                'icon_name': 'building',
                'link': '/services#rent',
                'order': 3
            },
            {
                'title': 'Home Loan',
                'description': 'Get assistance with home financing',
                'icon_name': 'dollar-sign',
                'link': '/services#loan',
                'order': 4
            }
        ]
        
        for card_data in cards:
            HeroCard.objects.create(**card_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(cards)} hero cards'))

    def create_how_it_works(self):
        """Create how it works steps"""
        self.stdout.write('Creating how it works steps...')
        steps = [
            {
                'number': 1,
                'title': 'Find Your Property',
                'description': 'Browse through our extensive collection of properties and find the one that matches your requirements.',
                'icon_name': 'search',
                'order': 1
            },
            {
                'number': 2,
                'title': 'Schedule a Visit',
                'description': 'Contact us to schedule a property visit at your convenience. Our agents will guide you through.',
                'icon_name': 'file-text',
                'order': 2
            },
            {
                'number': 3,
                'title': 'Get Your Keys',
                'description': 'Complete the paperwork and move into your dream home. We handle all the documentation.',
                'icon_name': 'key',
                'order': 3
            }
        ]
        
        for step_data in steps:
            HowItWorksStep.objects.create(**step_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(steps)} how it works steps'))

    def create_neighborhoods(self):
        """Create neighborhoods"""
        self.stdout.write('Creating neighborhoods...')
        neighborhoods = [
            {'name': 'Downtown', 'url': 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=400&h=300&fit=crop', 'order': 1},
            {'name': 'Suburbs', 'url': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop', 'order': 2},
            {'name': 'Waterfront', 'url': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=400&h=300&fit=crop', 'order': 3},
            {'name': 'Historic District', 'url': 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=300&fit=crop', 'order': 4},
            {'name': 'Business District', 'url': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&h=300&fit=crop', 'order': 5}
        ]
        
        for data in neighborhoods:
            neighborhood = Neighborhood.objects.create(
                name=data['name'],
                order=data['order']
            )
            image_content = self.download_image(data['url'])
            if image_content:
                neighborhood.image.save(f"{data['name'].lower().replace(' ', '-')}.jpg", image_content, save=True)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(neighborhoods)} neighborhoods'))

    def create_benefits(self):
        """Create benefits"""
        self.stdout.write('Creating benefits and gallery...')
        
        # Get or create BenefitsSection first
        benefits_section, _ = BenefitsSection.objects.get_or_create(
            defaults={
                'title': 'Why Choose Us',
                'description': 'My objective is to not only have a good impact on ourselves and our families but also to inspire, encourage, and affect long-term change in everyone we meet.',
                'phone': '+1 (321) 456 7890',
                'email': 'hello@example.com',
                'is_active': True
            }
        )
        
        benefits = [
            'Over 12 years of experience in real estate',
            'Personalized service for every client',
            'Expert knowledge of local markets',
            'Transparent and honest communication'
        ]
        
        for idx, text in enumerate(benefits, 1):
            Benefit.objects.create(
                benefits_section=benefits_section,
                text=text,
                order=idx
            )
        
        # Create gallery images
        gallery_urls = [
            'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop',
            'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=400&h=300&fit=crop',
            'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=400&h=300&fit=crop'
        ]
        
        for idx, url in enumerate(gallery_urls, 1):
            gallery = BenefitGalleryImage.objects.create(
                benefits_section=benefits_section,
                alt_text=f'Gallery Image {idx}',
                order=idx
            )
            image_content = self.download_image(url)
            if image_content:
                gallery.image.save(f'gallery-{idx}.jpg', image_content, save=True)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(benefits)} benefits and {len(gallery_urls)} gallery images'))

    def create_benefits_contact(self):
        """Create benefits section (already created in create_benefits)"""
        # This is now handled in create_benefits method
        pass

    def create_contact_section(self):
        """Create contact section settings"""
        self.stdout.write('Creating contact section settings...')
        contact, created = ContactSectionSettings.objects.get_or_create(
            defaults={
                'card_title': 'Looking for a dream home?',
                'card_subtitle': 'We can help you realize your dream',
                'card_description': 'Having your own home is everyone\'s dream. We are here to help you find the perfect property that matches your lifestyle and budget.',
                'button_text': 'Contact Me',
                'button_link': '/contact',
                'phone': '+1 (321) 456 7890',
                'email': 'hello@example.com',
                'is_active': True
            }
        )
        
        if created:
            image_url = 'https://www.realtorpal.hocud.com/wp-content/uploads/Realtor-Pal-Main-Agent-pro.png'
            image_content = self.download_image(image_url)
            if image_content:
                contact.person_image.save('contact-person.png', image_content, save=True)
        
        self.stdout.write(self.style.SUCCESS('✓ Contact section settings created'))

    def create_instagram_images(self):
        """Create instagram images"""
        self.stdout.write('Creating instagram images...')
        instagram_urls = [
            'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=300&h=300&fit=crop',
            'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=300&h=300&fit=crop',
            'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=300&h=300&fit=crop',
            'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=300&h=300&fit=crop',
            'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=300&h=300&fit=crop',
            'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=300&h=300&fit=crop',
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=300&h=300&fit=crop',
            'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=300&h=300&fit=crop'
        ]
        
        for idx, url in enumerate(instagram_urls, 1):
            instagram = InstagramImage.objects.create(
                link='https://instagram.com',
                alt_text=f'Instagram Post {idx}',
                order=idx
            )
            image_content = self.download_image(url)
            if image_content:
                instagram.image.save(f'instagram-{idx}.jpg', image_content, save=True)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(instagram_urls)} instagram images'))

    def create_person_section(self):
        """Create person section settings"""
        self.stdout.write('Creating person section settings...')
        person, created = PersonSectionSettings.objects.get_or_create(
            defaults={
                'title': 'I will help you in every way possible to locate your next residence.',
                'description': 'Since 2010, I have assisted over 1500 customers in saving over $85 million on their real estate transactions. I provide customers with a personalized experience for selling, purchasing, and renting properties, as well as assistance in obtaining a home loan, with complete transparency and flawless service.',
                'button_text': 'Contact Me',
                'button_link': '/contact',
                'phone': '+1 (321) 456 7890',
                'email': 'hello@example.com',
                'is_active': True
            }
        )
        
        if created:
            image_url = 'https://www.realtorpal.hocud.com/wp-content/uploads/Realtor-Pal-Main-Agent-pro.png'
            image_content = self.download_image(image_url)
            if image_content:
                person.person_image.save('person.png', image_content, save=True)
        
        self.stdout.write(self.style.SUCCESS('✓ Person section settings created'))

    def create_stats(self):
        """Create stats"""
        self.stdout.write('Creating stats...')
        stats = [
            {
                'icon_name': 'crown',
                'label': '12+ Years of Experience',
                'description': 'Nullam id dolor id nibh ultricies vehicula ut id elit. Cras justo odio, dapibus ac facilisis in, egestas eget quam.',
                'order': 1
            },
            {
                'icon_name': 'users',
                'label': '1500+ Satisfied Clients',
                'description': 'Nullam id dolor id nibh ultricies vehicula ut id elit. Cras justo odio, dapibus ac facilisis in, egestas eget quam.',
                'order': 2
            },
            {
                'icon_name': 'map-pinned',
                'label': '24 Locations Covered',
                'description': 'Nullam id dolor id nibh ultricies vehicula ut id elit. Cras justo odio, dapibus ac facilisis in, egestas eget quam.',
                'order': 3
            },
            {
                'icon_name': 'star',
                'label': '100+ Five Star Ratings',
                'description': 'Nullam id dolor id nibh ultricies vehicula ut id elit. Cras justo odio, dapibus ac facilisis in, egestas eget quam.',
                'order': 4
            }
        ]
        
        for stat_data in stats:
            StatItem.objects.create(**stat_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(stats)} stats'))
