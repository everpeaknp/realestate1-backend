from django.db import models
from blog.models import BlogPost


class GalleryImage(models.Model):
    """Media library for all images"""
    
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='gallery_images', null=True, blank=True)
    image = models.ImageField(upload_to='gallery/', help_text="Upload image")
    caption = models.CharField(max_length=200, blank=True, help_text="Optional image caption")
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alt text for accessibility")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Image'
        verbose_name_plural = 'Images'
    
    def __str__(self):
        if self.post:
            return f"Image for {self.post.title}"
        return f"Image - {self.image.name}"
    
    @property
    def file_size(self):
        """Get file size in KB"""
        try:
            return f"{self.image.size / 1024:.1f} KB"
        except:
            return "N/A"
    
    @property
    def file_name(self):
        """Get file name"""
        try:
            return self.image.name.split('/')[-1]
        except:
            return "N/A"
    
    def get_admin_url(self):
        """Get the admin change URL for this object"""
        from django.urls import reverse
        return reverse('admin:gallery_galleryimage_change', args=[self.pk])
