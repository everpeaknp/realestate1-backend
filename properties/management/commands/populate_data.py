"""
Management command to populate the database with sample data
Usage: python manage.py populate_data
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from properties.models import Property, PropertyImage
from leads.models import Lead, NewsletterSubscription
from blog.models import BlogPost, Comment
from testimonials.models import Testimonial
from projects.models import Project
from faqs.models import FAQ
from agents.models import Agent
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Populate database with sample data for Realtor Pal'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Create agents first (needed for properties)
        self.create_agents()
        
        # Create properties
        self.create_properties()
        
        # Create blog posts
        self.create_blog_posts()
        
        # Create testimonials
        self.create_testimonials()
        
        # Create projects
        self.create_projects()
        
        # Create FAQs
        self.create_faqs()
        
        # Create sample leads
        self.create_leads()
        
        self.stdout.write(self.style.SUCCESS('✅ Data population completed successfully!'))

    def create_agents(self):
        """Create sample agents"""
        agents_data = [
            {
                'name': 'Justin Nelson',
                'email': 'justin@realtorpal.com',
                'phone': '+1 (555) 123-4567',
                'bio': 'Experienced real estate professional with over 10 years in the industry. Specializing in residential properties and first-time home buyers.',
                'avatar': 'https://www.realtorpal.hocud.com/wp-content/uploads/Realtor-Pal-Main-Agent-pro.png',
                'specialties': ['Residential Sales', 'First-Time Buyers', 'Investment Properties'],
                'facebook': 'https://facebook.com/justinnelson',
                'twitter': 'https://twitter.com/justinnelson',
                'instagram': 'https://instagram.com/justinnelson',
                'linkedin': 'https://linkedin.com/in/justinnelson',
                'is_active': True
            },
            {
                'name': 'Sarah Mitchell',
                'email': 'sarah@realtorpal.com',
                'phone': '+1 (555) 234-5678',
                'bio': 'Luxury property specialist with a passion for helping clients find their dream homes. Expert in high-end residential and commercial properties.',
                'avatar': 'https://www.realtorpal.hocud.com/wp-content/uploads/Realtor-Pal-Main-Agent-pro.png',
                'specialties': ['Luxury Homes', 'Commercial Properties', 'Property Investment'],
                'facebook': 'https://facebook.com/sarahmitchell',
                'instagram': 'https://instagram.com/sarahmitchell',
                'linkedin': 'https://linkedin.com/in/sarahmitchell',
                'is_active': True
            }
        ]
        
        for agent_data in agents_data:
            agent, created = Agent.objects.get_or_create(
                email=agent_data['email'],
                defaults=agent_data
            )
            if created:
                self.stdout.write(f'  ✓ Created agent: {agent.name}')

    def create_properties(self):
        """Create sample properties"""
        agents = list(Agent.objects.all())
        
        properties_data = [
            {
                'title': 'Modern Family Home in Merril Willow',
                'description': 'Beautiful 4-bedroom family home with spacious backyard, modern kitchen, and excellent school district. Perfect for growing families.',
                'address': '123 Willow Street',
                'city': 'Merril Willow',
                'state': 'CA',
                'zip_code': '90210',
                'price': 186000,
                'property_type': 'FOR_SALE',
                'status': 'AVAILABLE',
                'beds': 4,
                'baths': 3,
                'garage': 2,
                'sqft': 2500,
                'year_built': 2018,
                'lot_size': 5000,
                'amenities': 'Swimming Pool, Garden, Modern Kitchen, Walk-in Closet, Hardwood Floors, Central AC',
                'is_featured': True
            },
            {
                'title': 'Luxury Downtown Condo',
                'description': 'Stunning 2-bedroom condo in the heart of downtown with panoramic city views, high-end finishes, and building amenities.',
                'address': '456 Main Street, Unit 1205',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90012',
                'price': 125000,
                'property_type': 'FOR_RENT',
                'status': 'AVAILABLE',
                'beds': 2,
                'baths': 2,
                'garage': 1,
                'sqft': 1200,
                'year_built': 2020,
                'amenities': 'Gym, Pool, Concierge, Rooftop Terrace, Pet Friendly',
                'is_featured': True
            },
            {
                'title': 'Charming Victorian House',
                'description': 'Historic Victorian home with original details, updated systems, and beautiful gardens. A rare find in a sought-after neighborhood.',
                'address': '789 Heritage Lane',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94102',
                'price': 295000,
                'property_type': 'FOR_SALE',
                'status': 'AVAILABLE',
                'beds': 5,
                'baths': 4,
                'garage': 2,
                'sqft': 3500,
                'year_built': 1895,
                'lot_size': 6000,
                'amenities': 'Historic Details, Garden, Updated Kitchen, Wine Cellar, Fireplace',
                'is_featured': True
            },
            {
                'title': 'Beachfront Paradise',
                'description': 'Wake up to ocean views in this stunning beachfront property. Direct beach access, modern amenities, and coastal living at its finest.',
                'address': '321 Ocean Drive',
                'city': 'Malibu',
                'state': 'CA',
                'zip_code': '90265',
                'price': 450000,
                'property_type': 'FOR_SALE',
                'status': 'AVAILABLE',
                'beds': 4,
                'baths': 4,
                'garage': 3,
                'sqft': 4000,
                'year_built': 2019,
                'lot_size': 8000,
                'amenities': 'Beach Access, Ocean View, Infinity Pool, Outdoor Kitchen, Smart Home',
                'is_featured': True
            },
            {
                'title': 'Cozy Suburban Starter Home',
                'description': 'Perfect starter home in a quiet neighborhood. Well-maintained, move-in ready, and close to schools and shopping.',
                'address': '555 Maple Avenue',
                'city': 'Pasadena',
                'state': 'CA',
                'zip_code': '91101',
                'price': 89000,
                'property_type': 'FOR_SALE',
                'status': 'AVAILABLE',
                'beds': 3,
                'baths': 2,
                'garage': 1,
                'sqft': 1500,
                'year_built': 2010,
                'lot_size': 3000,
                'amenities': 'Backyard, Updated Appliances, Central Heating',
                'is_featured': False
            },
            {
                'title': 'Spacious Ranch Style Home',
                'description': 'Single-story ranch with open floor plan, large lot, and RV parking. Great for entertaining and outdoor activities.',
                'address': '888 Ranch Road',
                'city': 'Santa Barbara',
                'state': 'CA',
                'zip_code': '93101',
                'price': 215000,
                'property_type': 'FOR_SALE',
                'status': 'AVAILABLE',
                'beds': 4,
                'baths': 3,
                'garage': 3,
                'sqft': 2800,
                'year_built': 2015,
                'lot_size': 10000,
                'amenities': 'RV Parking, Large Lot, Open Floor Plan, Patio',
                'is_featured': False
            },
            {
                'title': 'Modern Loft Apartment',
                'description': 'Industrial-chic loft in converted warehouse. High ceilings, exposed brick, and trendy neighborhood.',
                'address': '222 Industrial Way, Loft 3B',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90021',
                'price': 95000,
                'property_type': 'FOR_RENT',
                'status': 'AVAILABLE',
                'beds': 1,
                'baths': 1,
                'garage': 1,
                'sqft': 900,
                'year_built': 2017,
                'amenities': 'Exposed Brick, High Ceilings, Modern Fixtures, Bike Storage',
                'is_featured': False
            },
            {
                'title': 'Family Estate with Pool',
                'description': 'Luxurious family estate with resort-style pool, outdoor kitchen, and guest house. Perfect for entertaining.',
                'address': '999 Estate Drive',
                'city': 'Beverly Hills',
                'state': 'CA',
                'zip_code': '90210',
                'price': 675000,
                'property_type': 'FOR_SALE',
                'status': 'AVAILABLE',
                'beds': 6,
                'baths': 5,
                'garage': 4,
                'sqft': 6000,
                'year_built': 2021,
                'lot_size': 15000,
                'amenities': 'Pool, Guest House, Outdoor Kitchen, Home Theater, Wine Cellar',
                'is_featured': False
            }
        ]
        
        for prop_data in properties_data:
            # Assign random agent
            prop_data['agent'] = random.choice(agents)
            
            # Create slug from title
            prop_data['slug'] = slugify(prop_data['title'])
            
            property_obj, created = Property.objects.get_or_create(
                slug=prop_data['slug'],
                defaults=prop_data
            )
            
            if created:
                self.stdout.write(f'  ✓ Created property: {property_obj.title}')

    def create_blog_posts(self):
        """Create sample blog posts"""
        posts_data = [
            {
                'title': '10 Tips for First-Time Home Buyers',
                'excerpt': 'Essential advice for navigating your first home purchase with confidence.',
                'content': '<p>Buying your first home is an exciting milestone, but it can also be overwhelming. Here are 10 essential tips to help you navigate the process...</p><p>1. Get pre-approved for a mortgage before house hunting...</p>',
                'category': 'Buying Tips',
                'tags': 'first-time buyers, home buying, mortgage, tips',
                'author_name': 'Justin Nelson',
                'is_published': True
            },
            {
                'title': 'How to Stage Your Home for a Quick Sale',
                'excerpt': 'Professional staging tips that help sell homes faster and for more money.',
                'content': '<p>Home staging is one of the most effective ways to sell your property quickly and at a higher price. Here\'s what you need to know...</p>',
                'category': 'Selling Tips',
                'tags': 'home staging, selling, real estate tips',
                'author_name': 'Sarah Mitchell',
                'is_published': True
            },
            {
                'title': 'Understanding Real Estate Market Trends in 2026',
                'excerpt': 'An in-depth analysis of current market conditions and what they mean for buyers and sellers.',
                'content': '<p>The real estate market in 2026 is showing interesting trends. Let\'s break down what\'s happening and what it means for you...</p>',
                'category': 'Market Analysis',
                'tags': 'market trends, real estate, 2026, analysis',
                'author_name': 'Justin Nelson',
                'is_published': True
            },
            {
                'title': 'The Benefits of Working with a Real Estate Agent',
                'excerpt': 'Why professional representation matters in today\'s competitive market.',
                'content': '<p>In today\'s fast-paced real estate market, having a professional agent on your side can make all the difference...</p>',
                'category': 'Industry Insights',
                'tags': 'real estate agent, professional help, buying, selling',
                'author_name': 'Sarah Mitchell',
                'is_published': True
            }
        ]
        
        for post_data in posts_data:
            post_data['slug'] = slugify(post_data['title'])
            post_data['published_at'] = datetime.now() - timedelta(days=random.randint(1, 30))
            
            post, created = BlogPost.objects.get_or_create(
                slug=post_data['slug'],
                defaults=post_data
            )
            
            if created:
                self.stdout.write(f'  ✓ Created blog post: {post.title}')

    def create_testimonials(self):
        """Create sample testimonials"""
        testimonials_data = [
            {
                'client_name': 'John & Mary Smith',
                'rating': 5,
                'content': 'Justin helped us find our dream home! His knowledge of the market and dedication to finding the perfect property was outstanding. Highly recommended!',
                'property_type': 'Family Home',
                'is_approved': True,
                'is_featured': True
            },
            {
                'client_name': 'Robert Johnson',
                'rating': 5,
                'content': 'Sarah made selling our home a breeze. She handled everything professionally and we got above asking price. Couldn\'t be happier!',
                'property_type': 'Condo',
                'is_approved': True,
                'is_featured': True
            },
            {
                'client_name': 'Emily Davis',
                'rating': 5,
                'content': 'As a first-time buyer, I was nervous about the process. The team at Realtor Pal guided me every step of the way. Thank you!',
                'property_type': 'Starter Home',
                'is_approved': True,
                'is_featured': False
            },
            {
                'client_name': 'Michael Brown',
                'rating': 4,
                'content': 'Great experience working with this team. They were responsive, knowledgeable, and helped us find exactly what we were looking for.',
                'property_type': 'Investment Property',
                'is_approved': True,
                'is_featured': False
            }
        ]
        
        for testimonial_data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                client_name=testimonial_data['client_name'],
                defaults=testimonial_data
            )
            
            if created:
                self.stdout.write(f'  ✓ Created testimonial from: {testimonial.client_name}')

    def create_projects(self):
        """Create sample projects"""
        projects_data = [
            {
                'title': 'Willow Creek Development',
                'description': 'A modern residential community featuring 50 luxury homes with community amenities including pool, clubhouse, and parks.',
                'location': 'Merril Willow, CA',
                'completion_date': datetime.now() - timedelta(days=180),
                'category': 'Residential Development',
                'is_featured': True
            },
            {
                'title': 'Downtown Loft Conversion',
                'description': 'Historic warehouse converted into 30 modern loft apartments, preserving original architecture while adding contemporary amenities.',
                'location': 'Los Angeles, CA',
                'completion_date': datetime.now() - timedelta(days=90),
                'category': 'Commercial to Residential',
                'is_featured': True
            },
            {
                'title': 'Seaside Villas',
                'description': 'Exclusive beachfront villa community with 12 luxury properties, each with private beach access and ocean views.',
                'location': 'Malibu, CA',
                'completion_date': datetime.now() - timedelta(days=365),
                'category': 'Luxury Residential',
                'is_featured': False
            }
        ]
        
        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                title=project_data['title'],
                defaults=project_data
            )
            
            if created:
                self.stdout.write(f'  ✓ Created project: {project.title}')

    def create_faqs(self):
        """Create sample FAQs"""
        faqs_data = [
            {
                'question': 'How much do I need for a down payment?',
                'answer': 'Typically, you\'ll need 3-20% of the home\'s purchase price for a down payment. First-time buyers may qualify for programs requiring as little as 3% down.',
                'category': 'Buying',
                'order': 1
            },
            {
                'question': 'How long does it take to sell a home?',
                'answer': 'The average time to sell a home varies by market conditions, but typically ranges from 30-90 days. Proper pricing and staging can significantly reduce this time.',
                'category': 'Selling',
                'order': 2
            },
            {
                'question': 'What is the difference between pre-qualification and pre-approval?',
                'answer': 'Pre-qualification is an estimate of what you can afford based on self-reported information. Pre-approval involves a thorough review of your finances and is more reliable.',
                'category': 'Financing',
                'order': 3
            },
            {
                'question': 'Do I need a real estate agent?',
                'answer': 'While not required, a real estate agent provides valuable expertise, market knowledge, negotiation skills, and handles complex paperwork, often at no direct cost to buyers.',
                'category': 'General',
                'order': 4
            },
            {
                'question': 'What are closing costs?',
                'answer': 'Closing costs are fees associated with finalizing a real estate transaction, typically 2-5% of the purchase price. They include appraisal fees, title insurance, and loan origination fees.',
                'category': 'Buying',
                'order': 5
            },
            {
                'question': 'Should I get a home inspection?',
                'answer': 'Yes! A home inspection is highly recommended to identify potential issues before purchase. It typically costs $300-500 but can save thousands in unexpected repairs.',
                'category': 'Buying',
                'order': 6
            }
        ]
        
        for faq_data in faqs_data:
            faq, created = FAQ.objects.get_or_create(
                question=faq_data['question'],
                defaults=faq_data
            )
            
            if created:
                self.stdout.write(f'  ✓ Created FAQ: {faq.question[:50]}...')

    def create_leads(self):
        """Create sample leads"""
        leads_data = [
            {
                'first_name': 'Alice',
                'last_name': 'Williams',
                'email': 'alice@example.com',
                'phone': '+1 (555) 111-2222',
                'inquiry_type': 'BUYING',
                'location': 'Los Angeles, CA',
                'subject': 'Looking for family home',
                'message': 'I\'m interested in finding a 3-4 bedroom home in a good school district.',
                'source': 'CONTACT_FORM',
                'status': 'NEW'
            },
            {
                'first_name': 'Bob',
                'last_name': 'Taylor',
                'email': 'bob@example.com',
                'phone': '+1 (555) 333-4444',
                'inquiry_type': 'SELLING',
                'location': 'San Francisco, CA',
                'subject': 'Want to sell my condo',
                'message': 'I need help selling my 2-bedroom condo downtown.',
                'source': 'CONTACT_FORM',
                'status': 'CONTACTED'
            }
        ]
        
        for lead_data in leads_data:
            lead, created = Lead.objects.get_or_create(
                email=lead_data['email'],
                defaults=lead_data
            )
            
            if created:
                self.stdout.write(f'  ✓ Created lead: {lead.first_name} {lead.last_name}')
