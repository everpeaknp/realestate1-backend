from django.db import models


class HeaderSettings(models.Model):
    """Singleton model for header settings"""
    logo_image = models.ImageField(upload_to='cms/logos/', blank=True, null=True, help_text="Upload a custom logo image (optional)")
    logo_text = models.CharField(max_length=100, default="Lily White Realestate")
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
    logo_text = models.CharField(max_length=100, default="Lily White Realestate")
    phone_number = models.CharField(max_length=50, default="+1 (321) 456 7890")
    email = models.EmailField(default="hello@example.com")
    copyright_text = models.CharField(max_length=200, default="2026 Lily White Realestate. All rights reserved.")
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


class NewsletterSettings(models.Model):
    """Singleton model for newsletter section settings"""
    title = models.CharField(max_length=200, default="Subscribe to my newsletter")
    description = models.TextField(default="Get the most recent information on real estate.")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Newsletter Settings'
        verbose_name_plural = 'Newsletter Settings'
    
    def __str__(self):
        return "Newsletter Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and NewsletterSettings.objects.exists():
            existing = NewsletterSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class PropertySidebarSettings(models.Model):
    """Singleton model for property sidebar settings"""
    form_title = models.CharField(max_length=200, default="Contact For Your Real Estate Solutions")
    default_agent = models.ForeignKey(
        'agents.Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sidebar_settings',
        help_text="Default agent to display in property sidebar"
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Property Sidebar Settings'
        verbose_name_plural = 'Property Sidebar Settings'
    
    def __str__(self):
        return "Property Sidebar Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and PropertySidebarSettings.objects.exists():
            existing = PropertySidebarSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class PropertiesHeroSettings(models.Model):
    """Singleton model for properties page hero section"""
    title = models.CharField(max_length=200, default="Properties")
    subtitle = models.CharField(max_length=300, default="Find your dream homes with me.")
    background_image = models.ImageField(
        upload_to='cms/heroes/',
        blank=True,
        null=True,
        help_text="Hero background image (recommended: 1920x600px)"
    )
    background_image_url = models.URLField(
        max_length=500,
        blank=True,
        default="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=1920",
        help_text="Fallback to URL if no image uploaded"
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Properties Hero Settings'
        verbose_name_plural = 'Properties Hero Settings'
    
    def __str__(self):
        return "Properties Hero Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and PropertiesHeroSettings.objects.exists():
            existing = PropertiesHeroSettings.objects.first()
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
