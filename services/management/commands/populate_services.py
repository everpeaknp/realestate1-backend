from django.core.management.base import BaseCommand
from services.models import Service, ServiceFeature, ServicesHeroSettings


class Command(BaseCommand):
    help = 'Populate services with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating services...')
        
        # Create or update Services Hero Settings
        hero, created = ServicesHeroSettings.objects.get_or_create(
            id=1,
            defaults={
                'title': 'Our Services',
                'subtitle': 'Comprehensive Real Estate Solutions Tailored to Your Needs',
                'background_url': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=1920',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Services Hero Settings'))
        else:
            self.stdout.write(self.style.WARNING('→ Services Hero Settings already exists'))
        
        # Buy Property Service
        buy_service, created = Service.objects.get_or_create(
            slug='buy-property',
            defaults={
                'title': 'Buy Property',
                'description': 'Find your dream home with our expert guidance. We help you navigate the buying process from start to finish, ensuring you make the best investment decision.',
                'image_url': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=800',
                'layout': 'IMAGE_LEFT',
                'phone': '+1 (555) 123-4567',
                'email': 'buy@realestate.com',
                'button_text': 'Start Your Search',
                'is_active': True,
                'order': 1
            }
        )
        if created:
            ServiceFeature.objects.bulk_create([
                ServiceFeature(service=buy_service, text='Extensive property listings', order=1),
                ServiceFeature(service=buy_service, text='Expert market analysis', order=2),
                ServiceFeature(service=buy_service, text='Negotiation support', order=3),
                ServiceFeature(service=buy_service, text='Financing assistance', order=4),
            ])
            self.stdout.write(self.style.SUCCESS('✓ Created Buy Property service'))
        else:
            self.stdout.write(self.style.WARNING('→ Buy Property service already exists'))
        
        # Rent Property Service
        rent_service, created = Service.objects.get_or_create(
            slug='rent-property',
            defaults={
                'title': 'Rent Property',
                'description': 'Discover the perfect rental property that fits your lifestyle and budget. We offer a wide range of rental options with flexible terms.',
                'image_url': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&q=80&w=800',
                'layout': 'IMAGE_RIGHT',
                'phone': '+1 (555) 123-4568',
                'email': 'rent@realestate.com',
                'button_text': 'Browse Rentals',
                'is_active': True,
                'order': 2
            }
        )
        if created:
            ServiceFeature.objects.bulk_create([
                ServiceFeature(service=rent_service, text='Verified rental listings', order=1),
                ServiceFeature(service=rent_service, text='Flexible lease terms', order=2),
                ServiceFeature(service=rent_service, text='Quick application process', order=3),
                ServiceFeature(service=rent_service, text='Tenant support services', order=4),
            ])
            self.stdout.write(self.style.SUCCESS('✓ Created Rent Property service'))
        else:
            self.stdout.write(self.style.WARNING('→ Rent Property service already exists'))
        
        # Sell Property Service
        sell_service, created = Service.objects.get_or_create(
            slug='sell-property',
            defaults={
                'title': 'Sell Property',
                'description': 'Get the best value for your property with our proven marketing strategies and expert negotiation skills. We make selling hassle-free.',
                'image_url': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=800',
                'layout': 'IMAGE_LEFT',
                'phone': '+1 (555) 123-4569',
                'email': 'sell@realestate.com',
                'button_text': 'Get Free Valuation',
                'is_active': True,
                'order': 3
            }
        )
        if created:
            ServiceFeature.objects.bulk_create([
                ServiceFeature(service=sell_service, text='Professional property valuation', order=1),
                ServiceFeature(service=sell_service, text='Strategic marketing campaigns', order=2),
                ServiceFeature(service=sell_service, text='Expert negotiation', order=3),
                ServiceFeature(service=sell_service, text='Fast closing process', order=4),
            ])
            self.stdout.write(self.style.SUCCESS('✓ Created Sell Property service'))
        else:
            self.stdout.write(self.style.WARNING('→ Sell Property service already exists'))
        
        # Home Loan Service
        loan_service, created = Service.objects.get_or_create(
            slug='home-loan',
            defaults={
                'title': 'Home Loan',
                'description': 'Secure the best financing options for your property purchase. Our mortgage experts help you find competitive rates and favorable terms.',
                'image_url': 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&q=80&w=800',
                'layout': 'IMAGE_RIGHT',
                'phone': '+1 (555) 123-4570',
                'email': 'loans@realestate.com',
                'button_text': 'Apply Now',
                'is_active': True,
                'order': 4
            }
        )
        if created:
            ServiceFeature.objects.bulk_create([
                ServiceFeature(service=loan_service, text='Competitive interest rates', order=1),
                ServiceFeature(service=loan_service, text='Multiple lender options', order=2),
                ServiceFeature(service=loan_service, text='Pre-approval assistance', order=3),
                ServiceFeature(service=loan_service, text='Refinancing solutions', order=4),
            ])
            self.stdout.write(self.style.SUCCESS('✓ Created Home Loan service'))
        else:
            self.stdout.write(self.style.WARNING('→ Home Loan service already exists'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Services population completed!'))
