from django.db import models


class FAQsHeroSettings(models.Model):
    """Singleton model for FAQs page hero section"""
    title = models.CharField(max_length=200, default="Common Queries")
    subtitle = models.CharField(
        max_length=300,
        default="My only purpose is to deliver successful results.",
        help_text="Subtitle text displayed below the title"
    )
    background_image = models.ImageField(
        upload_to='faqs/heroes/',
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
        verbose_name = 'FAQs Hero Settings'
        verbose_name_plural = 'FAQs Hero Settings'
        ordering = ['-updated_at']
    
    def __str__(self):
        return "FAQs Hero Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and FAQsHeroSettings.objects.exists():
            existing = FAQsHeroSettings.objects.first()
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


class FAQ(models.Model):
    """FAQ model for frequently asked questions"""
    
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=100, default="General")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        indexes = [
            models.Index(fields=['category', 'order']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.question
