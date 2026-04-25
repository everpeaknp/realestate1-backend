from django.contrib import admin
from django.utils.html import format_html
from .models import BlogPost, Comment, BlogGalleryImage, BlogCategory, BlogTag, BlogHeroSettings


@admin.register(BlogHeroSettings)
class BlogHeroSettingsAdmin(admin.ModelAdmin):
    """Admin for Blog Hero Settings"""
    list_display = ['title', 'subtitle', 'is_active']
    
    fieldsets = (
        ('Hero Content', {
            'fields': ('title', 'subtitle')
        }),
        ('Background Image', {
            'fields': ('background_image', 'background_image_preview', 'background_image_url'),
            'description': 'Upload a custom background image or use the URL fallback'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('background_image_preview', 'created_at', 'updated_at')
    
    def background_image_preview(self, obj):
        if obj.background_image:
            return format_html(
                '<img src="{}" style="max-width: 600px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.background_image.url
            )
        elif obj.background_image_url:
            return format_html(
                '<img src="{}" style="max-width: 600px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" /><br><small style="color: #666;">Using fallback URL</small>',
                obj.background_image_url
            )
        return format_html('<p style="color: #999;">No image</p>')
    background_image_preview.short_description = 'Preview'
    
    def has_add_permission(self, request):
        # Only allow one instance (singleton pattern)
        return not BlogHeroSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False


class CommentInline(admin.TabularInline):
    """Inline admin for comments"""
    model = Comment
    extra = 0
    fields = ('author_name', 'author_email', 'content', 'status', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = True


class BlogGalleryImageInline(admin.TabularInline):
    """Inline admin for media images"""
    model = BlogGalleryImage
    extra = 1
    fields = ('image', 'image_preview', 'caption', 'alt_text', 'order')
    readonly_fields = ('image_preview',)
    can_delete = True
    verbose_name = 'Media Image'
    verbose_name_plural = 'Media Images'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return format_html('<p style="color: #999;">No image</p>')
    image_preview.short_description = 'Preview'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Enhanced admin for BlogPost model with Jazzmin optimization"""
    list_display = (
        'title', 'category_badge', 'author_name', 'is_published_icon', 
        'views_display', 'comments_count_display', 'published_at'
    )
    list_filter = ('is_published', 'category', 'published_at')
    search_fields = ('title', 'excerpt', 'content', 'author_name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'published_at', 'updated_at', 'featured_image_preview', 'author_avatar_preview')
    date_hierarchy = 'published_at'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'is_published')
        }),
        ('Author', {
            'fields': ('author_name', 'author_avatar', 'author_avatar_preview')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Featured Image', {
            'fields': ('featured_image', 'featured_image_preview')
        }),
        ('Statistics', {
            'fields': ('views', 'published_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [BlogGalleryImageInline, CommentInline]
    
    def category_badge(self, obj):
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.category
        )
    category_badge.short_description = 'Category'
    category_badge.admin_order_field = 'category'
    
    def is_published_icon(self, obj):
        if obj.is_published:
            return format_html('<span style="color: #28a745; font-size: 18px;">✓</span>')
        return format_html('<span style="color: #dc3545; font-size: 18px;">✗</span>')
    is_published_icon.short_description = 'Published'
    is_published_icon.admin_order_field = 'is_published'
    
    def views_display(self, obj):
        return format_html('<span style="color: #007bff;">👁 {}</span>', obj.views)
    views_display.short_description = 'Views'
    views_display.admin_order_field = 'views'
    
    def comments_count_display(self, obj):
        count = obj.comments_count
        return format_html('<span style="color: #6c757d;">💬 {}</span>', count)
    comments_count_display.short_description = 'Comments'
    
    def featured_image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.featured_image.url
            )
        return format_html('<p style="color: #999;">No image uploaded</p>')
    featured_image_preview.short_description = 'Featured Image Preview'
    
    def author_avatar_preview(self, obj):
        if obj.author_avatar:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.author_avatar.url
            )
        return format_html('<p style="color: #999;">No avatar uploaded</p>')
    author_avatar_preview.short_description = 'Author Avatar Preview'
    
    actions = ['publish_posts', 'unpublish_posts']
    
    def publish_posts(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} posts published.', 'success')
    publish_posts.short_description = '✓ Publish selected posts'
    
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} posts unpublished.', 'warning')
    unpublish_posts.short_description = '✗ Unpublish selected posts'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for comments with Jazzmin optimization"""
    list_display = ('author_name', 'post_link', 'status_badge', 'created_at', 'content_preview')
    list_filter = ('status', 'created_at')
    search_fields = ('author_name', 'author_email', 'content', 'post__title')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('Author Information', {
            'fields': ('author_name', 'author_email', 'author_avatar')
        }),
        ('Comment', {
            'fields': ('post', 'content', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def post_link(self, obj):
        return format_html(
            '<a href="/admin/blog/blogpost/{}/change/" style="color: #007bff; text-decoration: none;">{}</a>',
            obj.post.id,
            obj.post.title[:40] + '...' if len(obj.post.title) > 40 else obj.post.title
        )
    post_link.short_description = 'Post'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#ffc107',
            'APPROVED': '#28a745',
            'SPAM': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def content_preview(self, obj):
        preview = obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
        return format_html('<span style="color: #6c757d; font-style: italic;">{}</span>', preview)
    content_preview.short_description = 'Content'
    
    actions = ['approve_comments', 'mark_as_spam', 'mark_as_pending']
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(status='APPROVED')
        self.message_user(request, f'{updated} comments approved.', 'success')
    approve_comments.short_description = '✓ Approve selected comments'
    
    def mark_as_spam(self, request, queryset):
        updated = queryset.update(status='SPAM')
        self.message_user(request, f'{updated} comments marked as spam.', 'error')
    mark_as_spam.short_description = '⚠ Mark as spam'
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='PENDING')
        self.message_user(request, f'{updated} comments marked as pending.', 'warning')
    mark_as_pending.short_description = '⏳ Mark as pending'


@admin.register(BlogGalleryImage)
class BlogGalleryImageAdmin(admin.ModelAdmin):
    """WordPress-style Media Library Admin"""
    list_display = ('image_thumbnail', 'file_name_display', 'caption_preview', 'alt_text_preview', 'file_size_display', 'post_link', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ('caption', 'alt_text', 'image', 'post__title')
    readonly_fields = ('created_at', 'image_preview', 'file_size_display', 'image_url', 'file_dimensions')
    list_per_page = 20
    list_display_links = ('image_thumbnail', 'file_name_display')
    
    fieldsets = (
        ('Upload', {
            'fields': ('image', 'image_preview')
        }),
        ('Details', {
            'fields': ('caption', 'alt_text', 'post', 'order')
        }),
        ('File Information', {
            'fields': ('image_url', 'file_size_display', 'file_dimensions', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">📷</span>')
    image_thumbnail.short_description = ''
    
    def file_name_display(self, obj):
        if obj.image:
            name = obj.file_name
            return format_html(
                '<strong style="color: #2271b1;">{}</strong>',
                name[:40] + '...' if len(name) > 40 else name
            )
        return format_html('<span style="color: #999;">No file</span>')
    file_name_display.short_description = 'File'
    
    def file_size_display(self, obj):
        return obj.file_size
    file_size_display.short_description = 'Size'
    
    def image_url(self, obj):
        if obj.image:
            return format_html(
                '<input type="text" value="{}" readonly style="width: 100%; padding: 5px; border: 1px solid #ddd; border-radius: 3px;" onclick="this.select();" />',
                obj.image.url
            )
        return "N/A"
    image_url.short_description = 'File URL'
    
    def file_dimensions(self, obj):
        if obj.image:
            try:
                from PIL import Image
                img = Image.open(obj.image.path)
                return f"{img.width} × {img.height} pixels"
            except:
                return "N/A"
        return "N/A"
    file_dimensions.short_description = 'Dimensions'
    
    def post_link(self, obj):
        if obj.post:
            return format_html(
                '<a href="/admin/blog/blogpost/{}/change/" style="color: #2271b1; text-decoration: none;">📝 {}</a>',
                obj.post.id,
                obj.post.title[:25] + '...' if len(obj.post.title) > 25 else obj.post.title
            )
        return format_html('<span style="color: #999;">Not attached</span>')
    post_link.short_description = 'Attached to'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div style="text-align: center;"><img src="{}" style="max-height: 400px; max-width: 600px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" /></div>',
                obj.image.url
            )
        return format_html('<p style="color: #999;">No image uploaded</p>')
    image_preview.short_description = 'Preview'
    
    def caption_preview(self, obj):
        if obj.caption:
            preview = obj.caption[:30] + '...' if len(obj.caption) > 30 else obj.caption
            return format_html('<span style="color: #50575e;">{}</span>', preview)
        return format_html('<span style="color: #999;">—</span>')
    caption_preview.short_description = 'Caption'
    
    def alt_text_preview(self, obj):
        if obj.alt_text:
            preview = obj.alt_text[:30] + '...' if len(obj.alt_text) > 30 else obj.alt_text
            return format_html('<span style="color: #50575e;">{}</span>', preview)
        return format_html('<span style="color: #999;">—</span>')
    alt_text_preview.short_description = 'Alt Text'
    
    actions = ['detach_from_posts']
    
    def detach_from_posts(self, request, queryset):
        updated = queryset.update(post=None)
        self.message_user(request, f'{updated} media items detached from posts.', 'success')
    detach_from_posts.short_description = '🔗 Detach from posts'


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    """Admin for blog categories"""
    list_display = ('name', 'slug', 'order', 'posts_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('order',)
    list_per_page = 50
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'slug', 'description', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def posts_count(self, obj):
        count = obj.posts.count()
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">📝 {}</span>',
            count
        )
    posts_count.short_description = 'Posts'


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    """Admin for blog tags"""
    list_display = ('name', 'slug', 'posts_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    list_per_page = 50
    
    fieldsets = (
        ('Tag Information', {
            'fields': ('name', 'slug')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def posts_count(self, obj):
        count = obj.posts.count()
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">🏷️ {}</span>',
            count
        )
    posts_count.short_description = 'Posts'

