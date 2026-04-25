"""
Management command to populate test leads for analytics dashboard testing
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from leads.models import Lead


class Command(BaseCommand):
    help = 'Populate test leads for analytics dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of test leads to create (default: 100)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Clear existing test leads (optional - comment out if you want to keep existing data)
        # Lead.objects.all().delete()
        # self.stdout.write(self.style.WARNING('Cleared existing leads'))

        inquiry_types = ['BUYING', 'SELLING', 'RENTING', 'HOME_LOAN', 'GENERAL']
        sources = ['CONTACT_FORM', 'CHATBOT', 'PROPERTY_INQUIRY', 'NEWSLETTER', 'VALUATION']
        statuses = ['NEW', 'CONTACTED', 'QUALIFIED', 'CLOSED']
        locations = [
            'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
            'Phoenix, AZ', 'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA',
            'Dallas, TX', 'San Jose, CA', 'Austin, TX', 'Jacksonville, FL'
        ]
        
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 
                      'James', 'Mary', 'William', 'Patricia', 'Richard', 'Jennifer', 'Thomas']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
                     'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez']

        now = timezone.now()
        created_count = 0

        for i in range(count):
            # Random date within last 12 months
            days_ago = random.randint(0, 365)
            created_at = now - timedelta(days=days_ago)
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            lead = Lead.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=f"{first_name.lower()}.{last_name.lower()}{i}@example.com",
                phone=f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                inquiry_type=random.choice(inquiry_types),
                location=random.choice(locations),
                subject=f"Inquiry about {random.choice(['buying', 'selling', 'renting'])} property",
                message=f"I'm interested in {random.choice(['buying', 'selling', 'renting'])} a property in {random.choice(locations)}. Please contact me.",
                budget=f"${random.randint(200, 800)}K - ${random.randint(800, 1500)}K",
                property_type_interest=random.choice(['3BHK Apartment', 'House', 'Condo', 'Villa', 'Land']),
                source=random.choice(sources),
                status=random.choice(statuses),
                created_at=created_at,
                updated_at=created_at + timedelta(hours=random.randint(1, 48))
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} test leads')
        )
        self.stdout.write(
            self.style.SUCCESS('Analytics dashboard should now display data!')
        )
        self.stdout.write(
            self.style.WARNING(f'Visit: http://localhost:8000/admin/leads/lead/analytics/')
        )
