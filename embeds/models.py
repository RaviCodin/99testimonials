import uuid
from django.db import models
from projects.models import Project
from testimonials.models import Testimonial


class EmbedCategory(models.Model):
    category = models.CharField(max_length=255)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.category


class EmbedTemplate(models.Model):
    category = models.ForeignKey(
        EmbedCategory, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='embed_templates/')
    multiple = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class EmbedInstance(models.Model):
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='embed_instances')
    template = models.ForeignKey(
        EmbedTemplate, on_delete=models.CASCADE, related_name='embed_instances', null=True, blank=True)
    testimonials = models.ManyToManyField(
        Testimonial, related_name='embed_instances', blank=True)
    # customization
    primaryColor = models.CharField(max_length=7, default='#000000')
    backgroundColor = models.CharField(max_length=7, default='#ffffff')
    fontFamily = models.CharField(max_length=255, default='Arial')
    callToActionLabel = models.CharField(
        max_length=255, blank=True, default='Visit')
    callToActionUrl = models.URLField(
        blank=True, default='https://www.99testimonials.com')

    def __str__(self):
        return f"{self.project.name} - {self.name}"
