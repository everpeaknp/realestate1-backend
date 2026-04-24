from django.db import models


class ProjectsHeroSettings(models.Model):
    """Singleton model for projects page hero section"""
    title = models.CharField(max_length=200, default="Projects")
    subtitle = models.CharField(
        max_length=300,
        default="Your exquisite partners in finding home solutions",
        help_text="Subtitle text displayed below the title"
    )
    background_image = models.ImageField(
        upload_to='projects/heroes/',
        blank=True,
        null=True,
        help_text="Hero background image (recommended: 1920x600px)"
    )
    background_image_url = models.URLField(
        max_length=500,
        blank=True,
        default="https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&q=80&w=1920",
        help_text="Fallback to URL if no image uploaded"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Projects Hero Settings'
        verbose_name_plural = 'Projects Hero Settings'
        ordering = ['-updated_at']
    
    def __str__(self):
        return "Projects Hero Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and ProjectsHeroSettings.objects.exists():
            existing = ProjectsHeroSettings.objects.first()
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


class Project(models.Model):
    """Project model for showcasing completed projects"""
    
    CATEGORY_CHOICES = [
        ('RESIDENTIAL', 'Residential'),
        ('COMMERCIAL', 'Commercial'),
        ('RENOVATION', 'Renovation'),
        ('LUXURY', 'Luxury'),
        ('MODERN', 'Modern'),
        ('TRADITIONAL', 'Traditional'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    completion_date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='RESIDENTIAL')
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-completion_date']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        indexes = [
            models.Index(fields=['order', '-completion_date']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    """Project images with proper file handling"""
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/')
    title = models.CharField(max_length=200, blank=True)
    caption = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Project Image'
        verbose_name_plural = 'Project Images'
    
    def __str__(self):
        return f"{self.project.title} - Image {self.order}"
