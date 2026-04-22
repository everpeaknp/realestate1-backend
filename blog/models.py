from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator


class BlogPost(models.Model):
    """Blog post model for content marketing"""
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, help_text="Short description for listing pages")
    content = models.TextField(help_text="Full blog post content (supports HTML)")
    featured_image = models.URLField(max_length=500)
    
    # Author information
    author_name = models.CharField(max_length=100, default="Admin")
    author_avatar = models.URLField(max_length=500, blank=True, null=True)
    
    # Categorization
    category = models.CharField(max_length=100, default="Real Estate")
    tags = models.JSONField(default=list, blank=True, help_text="List of tags")
    
    # Metadata
    views = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def comments_count(self):
        return self.comments.filter(status='APPROVED').count()


class Comment(models.Model):
    """Comment model for blog posts"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('SPAM', 'Spam'),
    ]
    
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    
    # Author information
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    author_avatar = models.URLField(max_length=500, blank=True, null=True)
    
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['post', 'status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title}"
