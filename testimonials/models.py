from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class TestimonialsHeroSettings(models.Model):
    """Singleton model for testimonials page hero section"""
    title = models.CharField(max_length=200, default="Testimonials")
    subtitle = models.CharField(
        max_length=300,
        default="Helping you get more for your real estate.",
        help_text="Subtitle text displayed below the title"
    )
    background_image = models.ImageField(
        upload_to='testimonials/heroes/',
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
        verbose_name = 'Testimonials Hero Settings'
        verbose_name_plural = 'Testimonials Hero Settings'
        ordering = ['-updated_at']
    
    def __str__(self):
        return "Testimonials Hero Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and TestimonialsHeroSettings.objects.exists():
            existing = TestimonialsHeroSettings.objects.first()
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


class Testimonial(models.Model):
    """Testimonial model for client reviews"""
    
    ROLE_CHOICES = [
        ('BUYER', 'Happy Buyer'),
        ('SELLER', 'Happy Seller'),
        ('RENTER', 'Happy Renter'),
        ('LANDLORD', 'Happy Landlord'),
    ]
    
    title = models.CharField(max_length=200, help_text="Testimonial title (e.g., 'Brilliant Service')")
    name = models.CharField(max_length=100, help_text="Client name")
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='BUYER',
        help_text="Client role"
    )
    text = models.TextField(help_text="Testimonial content")
    image = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
        help_text="Client photo"
    )
    rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="YouTube or Vimeo URL for video testimonials"
    )
    is_approved = models.BooleanField(default=True, help_text="Show on website")
    is_featured = models.BooleanField(default=False, help_text="Feature on homepage")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers appear first)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        indexes = [
            models.Index(fields=['is_approved', 'is_featured']),
            models.Index(fields=['order', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.name} ({self.rating}★)"
