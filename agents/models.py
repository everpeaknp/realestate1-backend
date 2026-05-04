from django.db import models


class Agent(models.Model):
    """Agent model for real estate agents"""
    
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    avatar = models.URLField(max_length=500, blank=True, default='')
    avatar_image = models.ImageField(
        upload_to='agents/avatars/',
        blank=True,
        null=True,
        help_text='Upload an image file. If provided, this takes priority over the URL field above.'
    )
    bio = models.TextField()
    specialties = models.JSONField(default=list, help_text="List of specialties")
    
    # Social media links
    facebook = models.URLField(max_length=500, blank=True, null=True)
    twitter = models.URLField(max_length=500, blank=True, null=True)
    instagram = models.URLField(max_length=500, blank=True, null=True)
    linkedin = models.URLField(max_length=500, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'
    
    def __str__(self):
        return self.name
