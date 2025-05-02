from rest_framework import serializers
from .models import EmbedCategory, EmbedTemplate, EmbedInstance
from testimonials.models import Testimonial
from testimonials.serializers import TestimonialSerializer


class EmbedCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmbedCategory
        fields = ['id', 'category']


class EmbedTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmbedTemplate
        fields = ['id', 'category', 'name', 'image']


class EmbedInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmbedInstance
        fields = ['id', 'project', 'template',
                  'testimonials', 'name', 'description', 'primaryColor', 'backgroundColor', 'fontFamily', 'callToActionLabel', 'callToActionUrl']


class EmbedInstanceViewSerializer(serializers.ModelSerializer):
    testimonials = TestimonialSerializer(many=True, read_only=True)
    template_data = EmbedTemplateSerializer(source='template', read_only=True)

    class Meta:
        model = EmbedInstance
        fields = ['id', 'project', 'template',
                  'testimonials', 'name', 'description', 'template_data',
                  'primaryColor', 'backgroundColor', 'fontFamily',
                  'callToActionLabel', 'callToActionUrl']
