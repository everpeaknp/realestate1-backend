"""
Management command to populate HomeWorth settings with default data
"""
from django.core.management.base import BaseCommand
from homeworth.models import HomeWorthHeroSettings, HomeWorthFormSettings


class Command(BaseCommand):
    help = 'Populate HomeWorth settings with default data'

    def handle(self, *args, **options):
        self.stdout.write('Populating HomeWorth settings...')
        
        # Create or update Hero Settings
        hero_settings = HomeWorthHeroSettings.get_settings()
        hero_settings.title = "What's My Home Worth?"
        hero_settings.subtitle = "Get a free, accurate valuation of your property"
        hero_settings.background_image_url = "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=1920"
        hero_settings.is_active = True
        hero_settings.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Created/Updated Hero Settings: {hero_settings.title}')
        )
        
        # Create or update Form Settings
        form_settings = HomeWorthFormSettings.get_settings()
        form_settings.form_title = "Request Your Free Home Valuation"
        form_settings.form_description = "Fill out the form below and I'll provide you with a comprehensive market analysis of your property."
        form_settings.submit_button_text = "GET FREE VALUATION"
        form_settings.success_message = "Thank you! Your valuation request has been submitted. We'll contact you shortly."
        form_settings.is_active = True
        form_settings.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Created/Updated Form Settings: {form_settings.form_title}')
        )
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ HomeWorth settings populated successfully!')
        )
        self.stdout.write(
            self.style.WARNING('\nYou can now edit these settings in Django Admin:')
        )
        self.stdout.write('  - Hero Settings: http://localhost:8000/admin/homeworth/homeworthherosettings/')
        self.stdout.write('  - Form Settings: http://localhost:8000/admin/homeworth/homeworthformsettings/')
