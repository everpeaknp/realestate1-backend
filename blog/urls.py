from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet, CommentViewSet, BlogHeroSettingsViewSet

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet, basename='blogpost')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'hero-settings', BlogHeroSettingsViewSet, basename='blog-hero-settings')

urlpatterns = [
    path('', include(router.urls)),
]
