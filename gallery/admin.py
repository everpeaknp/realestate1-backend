from django.contrib import admin
from django.utils.html import format_html
from .models import GalleryImage


class GalleryImageInline(admin.TabularInline):
    """Inline admin for media images"""
    model = GalleryImage
    extra = 1
    fields = ('image', 'image_preview', 'caption', 'alt_text', 'order')
    readonly_fields = ('image_preview',)
    can_delete = True
    verbose_name = 'Image'
    verbose_name_plural = 'Images'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return format_html('<p style="color: #999;">No image</p>')
    image_preview.short_description = 'Preview'


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """WordPress-style Media Library Admin with List/Grid View"""
    list_display = ('image_thumbnail', 'file_name_display', 'caption_preview', 'alt_text_preview', 'file_size_display', 'post_link', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ('caption', 'alt_text', 'image', 'post__title')
    readonly_fields = ('created_at', 'image_preview', 'file_size_display', 'image_url', 'file_dimensions')
    list_per_page = 20
    list_display_links = ('image_thumbnail', 'file_name_display')
    change_list_template = 'admin/gallery/galleryimage/change_list.html'
    ordering = ('-created_at',)
    
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
        self.message_user(request, f'{updated} images detached from posts.', 'success')
    detach_from_posts.short_description = 'Detach from posts'
