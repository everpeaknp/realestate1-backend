from django.db import models


class AboutHeroSettings(models.Model):
    """Singleton model for about page hero section"""
    title = models.CharField(max_length=200, default="Hello, I'm Justin Nelson")
    subtitle = models.CharField(max_length=300, default="Boston's most acceptable realtor you can trust.")
    background_image = models.ImageField(
        upload_to='about/heroes/',
        blank=True,
        null=True,
        help_text="Hero background image (recommended: 1920x600px)"
    )
    background_image_url = models.URLField(
        max_length=500,
        blank=True,
        default="https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&q=80&w=1920",
        help_text="Fallback to URL if no image uploaded"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'About Hero Settings'
        verbose_name_plural = 'About Hero Settings'
    
    def __str__(self):
        return "About Hero Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and AboutHeroSettings.objects.exists():
            existing = AboutHeroSettings.objects.first()
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


class Goal(models.Model):
    """Goal cards for About page"""
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Show/hide this goal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'
        indexes = [
            models.Index(fields=['order', 'created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.title


class ServicesProvide(models.Model):
    """Services Provide section for About page (singleton)"""
    
    subtitle = models.CharField(max_length=200, default='Services I Provide')
    title = models.TextField(help_text="Main heading text")
    background_image = models.ImageField(
        upload_to='about/', 
        help_text="Background image (recommended: 1920x450px)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Services Provide Section'
        verbose_name_plural = 'Services Provide Section'
    
    def __str__(self):
        return "Services Provide Section"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and ServicesProvide.objects.exists():
            # If trying to create a new instance when one exists, update the existing one
            existing = ServicesProvide.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
