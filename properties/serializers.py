from rest_framework import serializers
from .models import Property, PropertyImage


class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'image_url', 'caption', 'order']

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class PropertyListSerializer(serializers.ModelSerializer):
    """Serializer for property list view"""
    location = serializers.SerializerMethodField()
    main_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'slug', 'title', 'description', 'location', 'price', 'property_type',
            'status', 'beds', 'baths', 'garage', 'sqft', 'main_image',
            'main_image_url', 'is_featured'
        ]

    def get_location(self, obj):
        return obj.location_display

    def get_main_image_url(self, obj):
        if not obj.main_image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.main_image.url)
        return obj.main_image.url


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Serializer for property detail view"""
    location = serializers.SerializerMethodField()
    amenities_list = serializers.ReadOnlyField()
    images = PropertyImageSerializer(many=True, read_only=True)
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    agent_email = serializers.EmailField(source='agent.email', read_only=True)
    agent_phone = serializers.CharField(source='agent.phone', read_only=True)
    agent_avatar = serializers.CharField(source='agent.avatar', read_only=True)
    agent_bio = serializers.CharField(source='agent.bio', read_only=True)
    main_image_url = serializers.SerializerMethodField()
    floor_plan_url = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'slug', 'title', 'description', 'address', 'city', 'state',
            'zip_code', 'location', 'latitude', 'longitude', 'price',
            'property_type', 'status', 'beds', 'baths', 'garage', 'sqft',
            'year_built', 'lot_size', 'main_image', 'main_image_url',
            'floor_plan', 'floor_plan_url', 'amenities_list', 'is_featured',
            'images', 'agent_name', 'agent_email', 'agent_phone',
            'agent_avatar', 'agent_bio', 'created_at', 'updated_at'
        ]

    def get_location(self, obj):
        return {
            'address': obj.address,
            'city': obj.city,
            'state': obj.state,
            'zip_code': obj.zip_code,
            'display': obj.location_display
        }

    def get_main_image_url(self, obj):
        if not obj.main_image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.main_image.url)
        return obj.main_image.url

    def get_floor_plan_url(self, obj):
        if not obj.floor_plan:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.floor_plan.url)
        return obj.floor_plan.url
