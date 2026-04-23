from django.db import models


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
