from django.db import models


class HomeWorthHeroSettings(models.Model):
    """Singleton model for home worth page hero section"""
    title = models.CharField(max_length=200, default="What's My Home Worth?")
    subtitle = models.CharField(
        max_length=300,
        default="Get a free, accurate valuation of your property",
        help_text="Subtitle text displayed below the title"
    )
    background_image = models.ImageField(
        upload_to='homeworth/heroes/',
        blank=True,
        null=True,
        help_text="Hero background image (recommended: 1920x600px)"
    )
    background_image_url = models.URLField(
        max_length=500,
        blank=True,
        default="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=1920",
        help_text="Fallback to URL if no image uploaded"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Home Worth Hero Settings'
        verbose_name_plural = 'Home Worth Hero Settings'
    
    def __str__(self):
        return "Home Worth Hero Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and HomeWorthHeroSettings.objects.exists():
            existing = HomeWorthHeroSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    @property
    def background_url(self):
        """Return uploaded image URL or fallback URL"""
        if self.background_image:
            return self.background_image.url
        return self.background_image_url


class HomeWorthFormSettings(models.Model):
    """Singleton model for home worth form section"""
    form_title = models.CharField(
        max_length=200,
        default="Request Your Free Home Valuation",
        help_text="Main form heading"
    )
    form_description = models.TextField(
        default="Fill out the form below and I'll provide you with a comprehensive market analysis of your property.",
        help_text="Description text below the form title"
    )
    submit_button_text = models.CharField(
        max_length=100,
        default="GET FREE VALUATION",
        help_text="Text displayed on the submit button"
    )
    success_message = models.TextField(
        default="Thank you! Your valuation request has been submitted. We'll contact you shortly.",
        help_text="Message shown after successful form submission"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Home Worth Form Settings'
        verbose_name_plural = 'Home Worth Form Settings'
    
    def __str__(self):
        return "Home Worth Form Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and HomeWorthFormSettings.objects.exists():
            existing = HomeWorthFormSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
