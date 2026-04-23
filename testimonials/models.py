from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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
