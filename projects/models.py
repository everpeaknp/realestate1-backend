from django.db import models


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
