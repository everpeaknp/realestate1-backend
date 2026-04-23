from django.db import models


class Service(models.Model):
    """Service model for managing service sections"""
    
    LAYOUT_CHOICES = [
        ('IMAGE_LEFT', 'Image on Left'),
        ('IMAGE_RIGHT', 'Image on Right'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly identifier (e.g., 'buy-property')")
    description = models.TextField(help_text="Main description text")
    image = models.ImageField(upload_to='services/', help_text="Service image (recommended: 640x700px)")
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='IMAGE_LEFT')
    phone = models.CharField(max_length=50, default='+1 (321) 456 7890')
    email = models.EmailField(default='hello@example.com')
    button_text = models.CharField(max_length=100, default='Contact Me')
    is_active = models.BooleanField(default=True, help_text="Show/hide this service")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        indexes = [
            models.Index(fields=['order', 'created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title


class ServiceFeature(models.Model):
    """Features/bullet points for each service"""
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
    text = models.CharField(max_length=300)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Service Feature'
        verbose_name_plural = 'Service Features'
    
    def __str__(self):
        return f"{self.service.title} - {self.text[:50]}"
