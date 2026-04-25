from django.db import models
from properties.models import Property


class Lead(models.Model):
    """Lead/Inquiry model for contact forms and chatbot"""
    
    INQUIRY_TYPE_CHOICES = [
        ('BUYING', 'Buying'),
        ('SELLING', 'Selling'),
        ('RENTING', 'Renting'),
        ('HOME_LOAN', 'Home Loan'),
        ('GENERAL', 'General'),
    ]
    
    SOURCE_CHOICES = [
        ('CONTACT_FORM',     'Contact Form'),
        ('CHATBOT',          'Chatbot'),
        ('PROPERTY_INQUIRY', 'Property Inquiry'),
        ('NEWSLETTER',       'Newsletter'),
        ('VALUATION',        "What's My Home Worth"),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONTACTED', 'Contacted'),
        ('QUALIFIED', 'Qualified'),
        ('CLOSED', 'Closed'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    # Inquiry Details
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPE_CHOICES)
    location = models.CharField(max_length=200, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()

    # Interest / Preferences (optional)
    budget = models.CharField(max_length=100, blank=True, help_text="e.g. $200,000 - $400,000")
    property_type_interest = models.CharField(max_length=100, blank=True, help_text="e.g. 3BHK apartment, house, land")
    
    # Property Images (for valuation requests)
    property_image_1 = models.ImageField(upload_to='leads/property_images/', blank=True, null=True, help_text="Property image 1")
    property_image_2 = models.ImageField(upload_to='leads/property_images/', blank=True, null=True, help_text="Property image 2")
    property_image_3 = models.ImageField(upload_to='leads/property_images/', blank=True, null=True, help_text="Property image 3")
    property_image_4 = models.ImageField(upload_to='leads/property_images/', blank=True, null=True, help_text="Property image 4")
    property_image_5 = models.ImageField(upload_to='leads/property_images/', blank=True, null=True, help_text="Property image 5")

    # Metadata
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    related_property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='inquiries')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.inquiry_type}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class NewsletterSubscription(models.Model):
    """Newsletter subscription model"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('UNSUBSCRIBED', 'Unsubscribed'),
    ]
    
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email
