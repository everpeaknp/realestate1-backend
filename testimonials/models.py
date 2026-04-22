from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Testimonial(models.Model):
    """Testimonial model for client reviews"""
    
    client_name = models.CharField(max_length=100)
    client_avatar = models.URLField(max_length=500, blank=True, null=True)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    content = models.TextField(help_text="Testimonial text")
    property_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="What they bought/sold/rented"
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="YouTube or Vimeo URL for video testimonials"
    )
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        indexes = [
            models.Index(fields=['is_approved', 'is_featured']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Testimonial by {self.client_name} ({self.rating}★)"
