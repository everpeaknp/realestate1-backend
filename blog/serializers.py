from rest_framework import serializers
from .models import BlogPost, Comment


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for blog comments"""
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author_name', 'author_email', 
            'author_avatar', 'content', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'status']


class BlogPostListSerializer(serializers.ModelSerializer):
    """Serializer for blog post listing"""
    
    comments_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'slug', 'title', 'excerpt', 'featured_image',
            'author_name', 'author_avatar', 'category', 'tags',
            'views', 'comments_count', 'published_at'
        ]
        read_only_fields = ['id', 'slug', 'views', 'comments_count', 'published_at']


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Serializer for single blog post with full content"""
    
    comments_count = serializers.IntegerField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'slug', 'title', 'excerpt', 'content', 'featured_image',
            'author_name', 'author_avatar', 'category', 'tags',
            'views', 'comments_count', 'comments', 'published_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'views', 'comments_count', 'published_at', 'updated_at']
