from rest_framework import serializers
from .models import Project, ProjectImage


class ProjectImageSerializer(serializers.ModelSerializer):
    """Serializer for project images"""
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'title', 'caption', 'order']
    
    def get_image(self, obj):
        """Return full URL for image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for projects"""
    
    images = serializers.SerializerMethodField()
    category = serializers.CharField(source='get_category_display')
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'images', 'location',
            'completion_date', 'category', 'is_featured', 'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_images(self, obj):
        """Serialize images with request context"""
        images = obj.images.all()
        return ProjectImageSerializer(images, many=True, context=self.context).data
