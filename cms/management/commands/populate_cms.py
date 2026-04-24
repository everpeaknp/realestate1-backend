from django.core.management.base import BaseCommand
from cms.models import HeaderSettings, NavigationLink, FooterSettings, FooterLink, NewsletterSettings, PropertySidebarSettings


class Command(BaseCommand):
    help = 'Populate CMS data with header and footer settings'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating CMS data...')
        
        # Create header settings (singleton)
        header_settings, created = HeaderSettings.objects.get_or_create(
            pk=1,
            defaults={
                'logo_text': 'Lily White Realestate',
                'phone_number': '+1 (321) 456 7890',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created header settings'))
        else:
            self.stdout.write(self.style.WARNING('Header settings already exist'))
        
        # Create navigation links
        navigation_links_data = [
            {'name': 'HOME', 'href': '/', 'order': 1},
            {'name': 'PROPERTIES', 'href': '/properties', 'order': 2},
            {'name': 'SERVICES', 'href': '/services', 'order': 3},
            {'name': 'ABOUT ME', 'href': '/about', 'order': 4},
            {'name': 'BLOG', 'href': '/blog', 'order': 5},
            {'name': 'CONTACT', 'href': '/contact', 'order': 6},
        ]
        
        for link_data in navigation_links_data:
            link, created = NavigationLink.objects.get_or_create(
                name=link_data['name'],
                defaults={**link_data, 'is_active': True}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created navigation link: {link.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Navigation link already exists: {link.name}'))
        
        # Create footer settings (singleton)
        footer_settings, created = FooterSettings.objects.get_or_create(
            pk=1,
            defaults={
                'logo_text': 'Lily White Realestate',
                'phone_number': '+1 (321) 456 7890',
                'email': 'hello@example.com',
                'copyright_text': '2026 Lily White Realestate. All rights reserved.',
                'facebook_url': '#',
                'twitter_url': '#',
                'instagram_url': '#',
                'linkedin_url': '#',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created footer settings'))
        else:
            self.stdout.write(self.style.WARNING('Footer settings already exist'))
        
        # Create footer links
        footer_links_data = [
            {'name': "What's My Home Worth?", 'href': '/home-worth', 'order': 1},
            {'name': 'Testimonials', 'href': '/testimonials', 'order': 2},
            {'name': 'FAQs', 'href': '/faqs', 'order': 3},
            {'name': 'Projects', 'href': '/projects', 'order': 4},
            {'name': 'Terms & Conditions', 'href': '#', 'order': 5},
            {'name': 'Privacy Policy', 'href': '#', 'order': 6},
        ]
        
        for link_data in footer_links_data:
            link, created = FooterLink.objects.get_or_create(
                name=link_data['name'],
                defaults={**link_data, 'is_active': True}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created footer link: {link.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Footer link already exists: {link.name}'))
        
        # Create newsletter settings (singleton)
        newsletter_settings, created = NewsletterSettings.objects.get_or_create(
            pk=1,
            defaults={
                'title': 'Subscribe to my newsletter',
                'description': 'Get the most recent information on real estate.',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created newsletter settings'))
        else:
            self.stdout.write(self.style.WARNING('Newsletter settings already exist'))
        
        # Create property sidebar settings (singleton)
        sidebar_settings, created = PropertySidebarSettings.objects.get_or_create(
            pk=1,
            defaults={
                'form_title': 'Contact For Your Real Estate Solutions',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created property sidebar settings'))
        else:
            self.stdout.write(self.style.WARNING('Property sidebar settings already exist'))
        
        # Set default agent if one exists and not already set
        if not sidebar_settings.default_agent:
            from agents.models import Agent
            first_agent = Agent.objects.filter(is_active=True).first()
            if first_agent:
                sidebar_settings.default_agent = first_agent
                sidebar_settings.save()
                self.stdout.write(self.style.SUCCESS(f'Set default agent: {first_agent.name}'))
            else:
                self.stdout.write(self.style.WARNING('No active agents found to set as default'))
        
        self.stdout.write(self.style.SUCCESS('CMS data population complete!'))
