from django.db import models
from django.utils.text import slugify
from agents.models import Agent


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
        ordering = ['order']
    
    def __str__(self):
        return f"{self.property.title} - Image {self.order}"
