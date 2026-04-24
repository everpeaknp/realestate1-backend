from rest_framework import serializers
from .models import (
    HeroSettings, HeroCard, HowItWorksStep, Neighborhood,
    Benefit, BenefitGalleryImage, BenefitsSection,
    ContactSectionSettings, InstagramImage, PersonSectionSettings, StatItem
)


class HeroSettingsSerializer(serializers.ModelSerializer):
    background_image = serializers.SerializerMethodField()

    class Meta:
        model = HeroSettings
        fields = [
            'id', 'title', 'subtitle', 'background_image',
            'primary_button_text', 'primary_button_link',
            'secondary_button_text', 'secondary_button_link',
            'is_active'
        ]

    def get_background_image(self, obj):
        if obj.background_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.background_image.url)
        return None


class HeroCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroCard
        fields = ['id', 'title', 'description', 'icon_name', 'link', 'order', 'is_active']


class HowItWorksStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = HowItWorksStep
        fields = ['id', 'number', 'title', 'description', 'icon_name', 'order', 'is_active']


class NeighborhoodSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Neighborhood
        fields = ['id', 'name', 'image', 'order', 'is_active']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ['id', 'text', 'order', 'is_active']


class BenefitGalleryImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = BenefitGalleryImage
        fields = ['id', 'image', 'alt_text', 'order', 'is_active']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None


class BenefitsSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenefitsSection
        fields = ['id', 'title', 'description', 'phone', 'email', 'is_active']


class ContactSectionSettingsSerializer(serializers.ModelSerializer):
    person_image = serializers.SerializerMethodField()

    class Meta:
        model = ContactSectionSettings
        fields = [
            'id', 'person_image', 'card_title', 'card_subtitle',
            'card_description', 'button_text', 'button_link',
            'phone', 'email', 'is_active'
        ]

    def get_person_image(self, obj):
        if obj.person_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.person_image.url)
        return None


class InstagramImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = InstagramImage
        fields = ['id', 'image', 'link', 'alt_text', 'order', 'is_active']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None


class PersonSectionSettingsSerializer(serializers.ModelSerializer):
    person_image = serializers.SerializerMethodField()

    class Meta:
        model = PersonSectionSettings
        fields = [
            'id', 'title', 'description', 'person_image',
            'button_text', 'button_link', 'phone', 'email', 'is_active'
        ]

    def get_person_image(self, obj):
        if obj.person_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.person_image.url)
        return None


class StatItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatItem
        fields = ['id', 'icon_name', 'label', 'description', 'order', 'is_active']
