from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import F, Q
from .models import BlogPost, Comment, BlogHeroSettings
from .serializers import (
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    CommentSerializer,
    BlogHeroSettingsSerializer
)


class BlogHeroSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for blog hero settings.
    Returns the singleton blog hero settings.
    """
    queryset = BlogHeroSettings.objects.filter(is_active=True)
    serializer_class = BlogHeroSettingsSerializer
    permission_classes = [AllowAny]


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for blog posts
    
    list: Get all published blog posts
    retrieve: Get single blog post by slug (increments view count)
    create: Create new blog post (admin only)
    update: Update blog post (admin only)
    destroy: Delete blog post (admin only)
    """
    
    queryset = BlogPost.objects.filter(is_published=True)
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'excerpt', 'content', 'author_name', 'category__name']
    ordering_fields = ['published_at', 'views', 'title']
    ordering = ['-published_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get single blog post and increment view count"""
        instance = self.get_object()
        
        # Increment view count
        BlogPost.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all unique categories"""
        categories = BlogPost.objects.filter(
            is_published=True
        ).values_list('category', flat=True).distinct()
        return Response({'categories': list(categories)})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search blog posts by title or content"""
        query = request.query_params.get('q', '')
        if query:
            posts = self.queryset.filter(
                title__icontains=query
            ) | self.queryset.filter(
                content__icontains=query
            )
        else:
            posts = self.queryset
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for blog comments
    
    list: Get all approved comments for a post
    create: Submit a new comment (pending approval)
    """
    
    queryset = Comment.objects.filter(status='APPROVED')
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        """Filter comments by post if post_id is provided"""
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post_id')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create a new comment (status will be PENDING by default)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {
                'message': 'Comment submitted successfully. It will be visible after approval.',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
