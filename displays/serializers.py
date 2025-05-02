
from rest_framework import serializers
from .models import Display, Template
from testimonials.serializers import Testimonial, TestimonialSerializer


class DisplaySerializer(serializers.ModelSerializer):
    testimonials = TestimonialSerializer(many=True, read_only=True)
    testimonial_ids = serializers.PrimaryKeyRelatedField(
        queryset=Testimonial.objects.all(), many=True, write_only=True, source='testimonials'
    )

    class Meta:
        model = Display
        fields = ['id', 'template', 'project', 'name',
                  'variables', 'testimonials', 'testimonial_ids', 'image', 'custom_subdomain', 'branding']

    def create(self, validated_data):
        testimonial_ids = validated_data.pop('testimonials', [])
        image = validated_data.pop('image', None)
        display = Display.objects.create(image=image, **validated_data)
        display.testimonials.set(testimonial_ids)
        return display

    def update(self, instance, validated_data):
        testimonial_ids = validated_data.pop('testimonials', [])
        image = validated_data.pop('image', None)
        instance = super().update(instance, validated_data)
        if image is not None:
            instance.image = image
        instance.testimonials.set(testimonial_ids)
        instance.save()
        return instance

    def partial_update(self, instance, validated_data):
        return self.update(instance, validated_data)


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['id', 'type', 'name', 'image', 'variables', 'multiple']
