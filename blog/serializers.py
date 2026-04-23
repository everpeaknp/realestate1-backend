from rest_framework import serializers
from .models import BlogPost, Comment, BlogGalleryImage


class BlogGalleryImageSerializer(serializers.ModelSerializer):
    """Serializer for blog gallery images"""
    
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogGalleryImage
        fields = ['id', 'image', 'caption', 'order']
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for blog comments"""
    
    author_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author_name', 'author_email', 
            'author_avatar', 'content', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'status']
    
    def get_author_avatar(self, obj):
        if obj.author_avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.author_avatar.url)
            return obj.author_avatar.url
        return None


class BlogPostListSerializer(serializers.ModelSerializer):
    """Serializer for blog post listing"""
    
    comments_count = serializers.IntegerField(read_only=True)
    featured_image = serializers.SerializerMethodField()
    author_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'slug', 'title', 'excerpt', 'featured_image',
            'author_name', 'author_avatar', 'category', 'tags',
            'views', 'comments_count', 'published_at'
        ]
        read_only_fields = ['id', 'slug', 'views', 'comments_count', 'published_at']
    
    def get_featured_image(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None
    
    def get_author_avatar(self, obj):
        if obj.author_avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.author_avatar.url)
            return obj.author_avatar.url
        return None


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Serializer for single blog post with full content"""
    
    comments_count = serializers.IntegerField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    gallery_images = BlogGalleryImageSerializer(many=True, read_only=True)
    featured_image = serializers.SerializerMethodField()
    author_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'slug', 'title', 'excerpt', 'content', 'featured_image',
            'author_name', 'author_avatar', 'category', 'tags',
            'views', 'comments_count', 'comments', 'gallery_images',
            'published_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'views', 'comments_count', 'published_at', 'updated_at']
    
    def get_featured_image(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None
    
    def get_author_avatar(self, obj):
        if obj.author_avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.author_avatar.url)
            return obj.author_avatar.url
        return None
