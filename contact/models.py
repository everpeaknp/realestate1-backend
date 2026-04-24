from django.db import models


class ContactCard(models.Model):
    """Contact information cards displayed on the contact page"""
    ICON_CHOICES = [
        ('phone', 'Phone'),
        ('map', 'Map Pin'),
        ('email', 'Email'),
    ]
    
    title = models.CharField(max_length=100, help_text="e.g., 'CALL ME', 'OFFICE ADDRESS', 'EMAIL ME'")
    value = models.CharField(max_length=200, help_text="e.g., '+1 (321) 456 7890', '324 King Avenue, Boston, USA'")
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='phone')
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Contact Card'
        verbose_name_plural = 'Contact Cards'
    
    def __str__(self):
        return f"{self.title} - {self.value}"


class ContactFormSettings(models.Model):
    """Singleton model for contact form settings"""
    intro_text = models.TextField(
        default="If you have any questions about the real estate market, I'd love to chat. Reach out below, and I'll get back to you shortly. I look forward to hearing from you.",
        help_text="Text displayed above the contact cards"
    )
    agent_name = models.CharField(max_length=100, default="Justin Nelson")
    agent_title = models.CharField(max_length=100, default="Boston Realtor")
    agent_image = models.ImageField(
        upload_to='contact/agents/',
        blank=True,
        null=True,
        help_text="Upload agent profile image"
    )
    facebook_url = models.URLField(max_length=200, blank=True, default="#")
    twitter_url = models.URLField(max_length=200, blank=True, default="#")
    instagram_url = models.URLField(max_length=200, blank=True, default="#")
    linkedin_url = models.URLField(max_length=200, blank=True, default="#")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Contact Form Settings'
        verbose_name_plural = 'Contact Form Settings'
    
    def __str__(self):
        return f"Contact Form Settings - {self.agent_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and ContactFormSettings.objects.exists():
            # If trying to create a new instance when one already exists, update the existing one
            existing = ContactFormSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
