from rest_framework import serializers
from .models import Testimonial, TestimonialImage, TestimonialVideo, Tag, Customer, TestimonialHighlight


class TestimonialImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestimonialImage
        fields = ['id', 'testimonial', 'image']


class TestimonialVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestimonialVideo
        fields = ['id', 'testimonial', 'video']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'uid', 'email', 'full_name', 'job_title',
                  'company', 'company_logo', 'website_url', 'avatar']


class TestimonialHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestimonialHighlight
        fields = ['id', 'start_index', 'end_index']


class TestimonialSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    highlights = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=False)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Testimonial
        fields = [
            'id', 'name', 'tagline', 'avatar', 'email', 'company', 'team',
            'company_logo', 'rating', 'title', 'testimonial', 'url', 'date',
            'created', 'modified', 'project', 'images', 'videos', 'highlights', 'approved', 'tags', 'customer', 'source', 'campaignId'
        ]
        extra_kwargs = {
            'avatar': {'allow_null': True, 'required': False},
            'company_logo': {'allow_null': True, 'required': False},
        }

    def get_images(self, obj):
        images = TestimonialImage.objects.filter(testimonial=obj)
        return TestimonialImageSerializer(images, many=True).data

    def get_videos(self, obj):
        videos = TestimonialVideo.objects.filter(testimonial=obj)
        return TestimonialVideoSerializer(videos, many=True).data

    def get_highlights(self, obj):
        highlights = TestimonialHighlight.objects.filter(testimonial=obj)
        return TestimonialHighlightSerializer(highlights, many=True).data

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        tags_data = validated_data.pop('tags', [])
        testimonial = Testimonial.objects.create(**validated_data)
        for image_data in images_data:
            TestimonialImage.objects.create(
                testimonial=testimonial, **image_data)
        for tag in tags_data:
            testimonial.tags.add(tag)
        return testimonial

    def update(self, instance, validated_data):
        print("we are here")
        images_data = validated_data.pop('images', [])
        tags_data = validated_data.pop('tags', [])

        instance = super().update(instance, validated_data)

        # Update tags
        instance.tags.clear()
        for tag in tags_data:
            instance.tags.add(tag)

        # Update images
        # instance.images.all().delete()
        # for image_data in images_data:
        #     TestimonialImage.objects.create(testimonial=instance, **image_data)

        return instance


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
