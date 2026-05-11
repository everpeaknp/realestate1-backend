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

    # ── Filter Configuration ──
    show_filters = models.BooleanField(
        default=True,
        help_text="Show or hide the property filter bar"
    )
    filter_title = models.CharField(
        max_length=100,
        default="Filters",
        blank=True,
        help_text="Mobile toggle button label"
    )

    class Meta:
        verbose_name = 'Properties Hero Settings'
        verbose_name_plural = 'Properties Hero Settings'
    
    def __str__(self):
        return f"Properties Hero Settings - {self.title}"
    
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

class FilterOption(models.Model):
    """
    User-friendly way to manage filter options without editing JSON.
    """
    CATEGORY_CHOICES = [
        ('PROPERTY_TYPE', 'Property Type'),
        ('MIN_PRICE', 'Min Price'),
        ('MAX_PRICE', 'Max Price'),
        ('BEDROOMS', 'Bedrooms'),
        ('STATUS', 'Listing Status'),
    ]
    
    hero_settings = models.ForeignKey(
        PropertiesHeroSettings,
        on_delete=models.CASCADE,
        related_name='filter_options'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="The dropdown this option belongs to"
    )
    label = models.CharField(
        max_length=100,
        help_text="The text shown to the user (e.g. '$200,000' or '3+ Beds')"
    )
    value = models.CharField(
        max_length=100,
        help_text="The internal value sent to the API (e.g. '200000' or '3')"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Sort order in the dropdown"
    )

    class Meta:
        ordering = ['category', 'order', 'label']
        verbose_name = "Filter Option"
        verbose_name_plural = "Filter Options"

    def __str__(self):
        return f"[{self.get_category_display()}] {self.label}"

    
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
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    
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


class PropertyFeature(models.Model):
    """Property features/amenities"""
    
    FEATURE_CATEGORIES = [
        ('INTERIOR', 'Interior Features'),
        ('EXTERIOR', 'Exterior Features'),
        ('APPLIANCES', 'Appliances'),
        ('UTILITIES', 'Utilities'),
        ('COMMUNITY', 'Community Features'),
        ('OTHER', 'Other'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='features')
    category = models.CharField(max_length=20, choices=FEATURE_CATEGORIES, default='OTHER')
    name = models.CharField(max_length=100, help_text="Feature name (e.g., 'Hardwood Floors', 'Central AC')")
    icon = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Optional icon name (e.g., 'home', 'car', 'tree')"
    )
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Property Feature'
        verbose_name_plural = 'Property Features'
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return f"{self.property.title} - {self.name}"
