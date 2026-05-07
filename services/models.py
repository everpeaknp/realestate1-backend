from django.db import models
from django.utils.text import slugify


class Service(models.Model):
    """Service model for Buy, Sell, Rent, Home Loan services"""
    
    LAYOUT_CHOICES = [
        ('IMAGE_LEFT', 'Image Left'),
        ('IMAGE_RIGHT', 'Image Right'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(
        upload_to='services/',
        blank=True,
        null=True,
        help_text='Upload a service image'
    )
    image_url = models.URLField(
        max_length=500,
        blank=True,
        help_text='Or provide an external image URL (used if no image is uploaded)'
    )
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='IMAGE_LEFT')
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    button_text = models.CharField(max_length=100, default='Contact Me')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_image_url(self):
        """Return the image URL, prioritizing uploaded image over external URL"""
        if self.image:
            return self.image.url
        return self.image_url


class ServiceFeature(models.Model):
    """Features/bullet points for each service"""
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
    text = models.CharField(max_length=300)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Service Feature'
        verbose_name_plural = 'Service Features'
    
    def __str__(self):
        return f"{self.service.title} - {self.text[:50]}"


class ServicesHeroSettings(models.Model):
    """Hero section settings for Services page"""
    
    title = models.CharField(max_length=200, default='Our Services')
    subtitle = models.CharField(max_length=300, default='Comprehensive Real Estate Solutions')
    background_image = models.ImageField(
        upload_to='services/hero/',
        blank=True,
        null=True,
        help_text='Upload a background image for the services hero section'
    )
    background_url = models.URLField(
        max_length=500,
        blank=True,
        default='https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=1920',
        help_text='Or provide an external image URL (used if no image is uploaded)'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Services Hero Settings'
        verbose_name_plural = 'Services Hero Settings'
    
    def __str__(self):
        return f"Services Hero - {self.title}"
    
    def get_background_image_url(self):
        """Return the background image URL, prioritizing uploaded image over external URL"""
        if self.background_image:
            return self.background_image.url
        return self.background_url
