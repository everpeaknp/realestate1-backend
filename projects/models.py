from django.db import models


class Project(models.Model):
    """Project model for showcasing completed projects"""
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    images = models.JSONField(default=list, help_text="List of image URLs")
    location = models.CharField(max_length=200)
    completion_date = models.DateField()
    category = models.CharField(max_length=100, default="Residential")
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-completion_date']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        indexes = [
            models.Index(fields=['-completion_date']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return self.title
