from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from ckeditor_uploader.fields import RichTextUploadingField


class BlogHeroSettings(models.Model):
    """Singleton model for blog page hero section"""
    title = models.CharField(max_length=200, default="Blog")
    subtitle = models.CharField(max_length=300, blank=True, help_text="Optional subtitle text")
    background_image = models.ImageField(
        upload_to='blog/heroes/',
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
        verbose_name = 'Blog Hero Settings'
        verbose_name_plural = 'Blog Hero Settings'
    
    def __str__(self):
        return "Blog Hero Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and BlogHeroSettings.objects.exists():
            existing = BlogHeroSettings.objects.first()
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


class BlogCategory(models.Model):
    """Blog category model"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Category description")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogTag(models.Model):
    """Blog tag model"""
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    """Blog post model for content marketing"""
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, help_text="Short description for listing pages")
    content = RichTextUploadingField(
        config_name='blog',
        help_text="Full blog post content with rich text editor"
    )
    featured_image = models.ImageField(
        upload_to='blog/featured/',
        blank=True,
        null=True,
        help_text="Featured image for the blog post"
    )
    
    # Author information
    author_name = models.CharField(max_length=100, default="Admin")
    author_avatar = models.ImageField(
        upload_to='blog/avatars/',
        blank=True,
        null=True,
        help_text="Author avatar image"
    )
    
    # Categorization
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        help_text="Blog category"
    )
    tags = models.ManyToManyField(
        BlogTag,
        blank=True,
        related_name='posts',
        help_text="Blog tags"
    )
    
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
    author_avatar = models.ImageField(
        upload_to='blog/comment_avatars/',
        blank=True,
        null=True,
        help_text="Comment author avatar"
    )
    
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
