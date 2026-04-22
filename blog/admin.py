from django.contrib import admin
from django.utils.html import format_html
from .models import BlogPost, Comment


class CommentInline(admin.TabularInline):
    """Inline admin for comments"""
    model = Comment
    extra = 0
    fields = ('author_name', 'author_email', 'content', 'status', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = True


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
    readonly_fields = ('views', 'published_at', 'updated_at', 'featured_image_preview')
    date_hierarchy = 'published_at'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'is_published')
        }),
        ('Author', {
            'fields': ('author_name', 'author_avatar')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_preview')
        }),
        ('Statistics', {
            'fields': ('views', 'published_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CommentInline]
    
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
            return format_html('<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />', obj.featured_image)
        return format_html('<p style="color: #999;">No image</p>')
    featured_image_preview.short_description = 'Featured Image Preview'
    
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
