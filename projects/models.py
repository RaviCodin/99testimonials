import uuid
from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.utils import timezone


class Project(models.Model):
    owner = models.ForeignKey(
        User, related_name='owned_projects', on_delete=models.CASCADE)
    collaborators = models.ManyToManyField(
        User, related_name='collaborating_projects', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class TagCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    category = models.ForeignKey(
        TagCategory, related_name='tags', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(
        Project, related_name='tags', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='project_images/')

    def __str__(self):
        return f'Image {self.id}'


class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.FileField(upload_to='project_videos/')

    def __str__(self):
        return f'Video {self.id}'


class BrandLogo(models.Model):
    project = models.ForeignKey(
        Project, related_name='brand_logos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='brand_logos/')

    def __str__(self):
        return f'Logo {self.id}'


class BrandColor(models.Model):
    project = models.ForeignKey(
        Project, related_name='brand_colors', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return f'{self.name} ({self.hex_code})'


class BrandFont(models.Model):
    project = models.ForeignKey(
        Project, related_name='brand_fonts', on_delete=models.CASCADE)
    font_name = models.CharField(max_length=255)
    font_weight = models.CharField(default='400', max_length=5)

    def __str__(self):
        return f'{self.font_name} ({self.font_weight})'
