from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectsHeroSettingsViewSet

router = DefaultRouter()
router.register(r'hero', ProjectsHeroSettingsViewSet, basename='projects-hero')
router.register(r'', ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
]
