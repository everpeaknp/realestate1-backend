from django.core.management.base import BaseCommand
from contact.models import ContactCard, ContactFormSettings


class Command(BaseCommand):
    help = 'Populate contact cards and form settings with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating contact data...')
        
        # Create contact cards
        contact_cards_data = [
            {
                'title': 'CALL ME',
                'value': '+1 (321) 456 7890',
                'icon': 'phone',
                'order': 1,
                'is_active': True,
            },
            {
                'title': 'OFFICE ADDRESS',
                'value': '324 King Avenue, Boston, USA',
                'icon': 'map',
                'order': 2,
                'is_active': True,
            },
            {
                'title': 'EMAIL ME',
                'value': 'hello@example.com',
                'icon': 'email',
                'order': 3,
                'is_active': True,
            },
        ]
        
        for card_data in contact_cards_data:
            card, created = ContactCard.objects.get_or_create(
                title=card_data['title'],
                defaults=card_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created contact card: {card.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Contact card already exists: {card.title}'))
        
        # Create contact form settings (singleton)
        settings, created = ContactFormSettings.objects.get_or_create(
            pk=1,
            defaults={
                'intro_text': "If you have any questions about the real estate market, I'd love to chat. Reach out below, and I'll get back to you shortly. I look forward to hearing from you.",
                'agent_name': 'Justin Nelson',
                'agent_title': 'Boston Realtor',
                'agent_image': 'https://www.realtorpal.hocud.com/wp-content/uploads/Realtor-Pal-Main-Agent-pro.png',
                'facebook_url': '#',
                'twitter_url': '#',
                'instagram_url': '#',
                'linkedin_url': '#',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created contact form settings'))
        else:
            self.stdout.write(self.style.WARNING('Contact form settings already exist'))
        
        self.stdout.write(self.style.SUCCESS('Contact data population complete!'))
