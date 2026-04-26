from django.db import models
from django.utils.text import slugify
from agents.models import Agent


class PropertiesHeroSettings(models.Model):
    """Singleton model for properties page hero section"""
    title = models.CharField(max_length=200, default="Properties")
    subtitle = models.CharField(max_length=300, default="Find your dream homes with me.")
    background_image = models.ImageField(
        upload_to='properties/heroes/',
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
        verbose_name = 'Hero Settings'
        verbose_name_plural = 'Hero Settings'
    
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


class Property(models.Model):
    """Property model for real estate listings"""
    
    TYPE_CHOICES = [
        ('FOR_SALE', 'For Sale'),
        ('FOR_RENT', 'For Rent'),
    ]
    
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('PENDING', 'Pending'),
        ('SOLD', 'Sold'),
        ('RENTED', 'Rented'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    
    # Location
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2)
    property_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    
    # Features
    beds = models.IntegerField()
    baths = models.DecimalField(max_digits=3, decimal_places=1)
    garage = models.IntegerField(default=0)
    sqft = models.IntegerField()
    year_built = models.IntegerField(null=True, blank=True)
    lot_size = models.IntegerField(null=True, blank=True, help_text="In square feet")
    
    # Images
    main_image = models.ImageField(upload_to='properties/main/', null=True, blank=True)
    floor_plan = models.ImageField(upload_to='properties/floorplans/', null=True, blank=True)
    
    # Additional Info
    amenities = models.TextField(help_text="Comma-separated amenities", blank=True)
    is_featured = models.BooleanField(default=False)
    
    # Relationships
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, related_name='properties')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = "Properties"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def location_display(self):
        return f"{self.city}, {self.state}"
    
    @property
    def amenities_list(self):
        return [a.strip() for a in self.amenities.split(',') if a.strip()]


class PropertyImage(models.Model):
    """Additional images for properties"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.property.title} - Image {self.order}"
