from rest_framework import serializers
from .models import Project, Image, BrandColor, BrandFont, BrandLogo


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'owner', 'collaborators',
                  'created', 'modified', 'name', 'description', 'url']
        extra_kwargs = {
            'owner': {'read_only': True}  # Make owner read-only
        }


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']


class BrandLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandLogo
        fields = ['id', 'project', 'image']


class BrandColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandColor
        fields = ['id', 'project', 'name', 'hex_code']


class BrandFontSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandFont
        fields = ['id', 'project', 'font_name', 'font_weight']
