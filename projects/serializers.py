from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for projects"""
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'images', 'location',
            'completion_date', 'category', 'is_featured', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
