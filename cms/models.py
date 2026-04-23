from django.db import models


class HeaderSettings(models.Model):
    """Singleton model for header settings"""
    logo_image = models.ImageField(upload_to='cms/logos/', blank=True, null=True, help_text="Upload a custom logo image (optional)")
    logo_text = models.CharField(max_length=100, default="Realtor Pal")
    phone_number = models.CharField(max_length=50, default="+1 (321) 456 7890")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Header Settings'
        verbose_name_plural = 'Header Settings'
    
    def __str__(self):
        return f"Header Settings - {self.logo_text}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and HeaderSettings.objects.exists():
            existing = HeaderSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class NavigationLink(models.Model):
    """Navigation links for the header"""
    name = models.CharField(max_length=50, help_text="e.g., 'HOME', 'PROPERTIES', 'SERVICES'")
    href = models.CharField(max_length=200, help_text="e.g., '/', '/properties', '/services'")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Navigation Link'
        verbose_name_plural = 'Navigation Links'
    
    def __str__(self):
        return f"{self.name} ({self.href})"


class FooterSettings(models.Model):
    """Singleton model for footer settings"""
    logo_image = models.ImageField(upload_to='cms/logos/', blank=True, null=True, help_text="Upload a custom logo image (optional)")
    logo_text = models.CharField(max_length=100, default="Realtor Pal")
    phone_number = models.CharField(max_length=50, default="+1 (321) 456 7890")
    email = models.EmailField(default="hello@example.com")
    copyright_text = models.CharField(max_length=200, default="2026 Realtor Pal. All rights reserved.")
    facebook_url = models.URLField(max_length=200, blank=True, default="#")
    twitter_url = models.URLField(max_length=200, blank=True, default="#")
    instagram_url = models.URLField(max_length=200, blank=True, default="#")
    linkedin_url = models.URLField(max_length=200, blank=True, default="#")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Footer Settings'
        verbose_name_plural = 'Footer Settings'
    
    def __str__(self):
        return f"Footer Settings - {self.logo_text}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and FooterSettings.objects.exists():
            existing = FooterSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class FooterLink(models.Model):
    """Footer links"""
    name = models.CharField(max_length=100, help_text="e.g., 'What's My Home Worth?', 'Testimonials'")
    href = models.CharField(max_length=200, help_text="e.g., '/home-worth', '/testimonials'")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Footer Link'
        verbose_name_plural = 'Footer Links'
    
    def __str__(self):
        return f"{self.name} ({self.href})"
