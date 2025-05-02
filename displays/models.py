from django.db import models
from projects.models import Project
import uuid
from testimonials.models import Testimonial
from .utils import take_screenshot
# Create your models here.

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
import io


class Template(models.Model):
    TYPE_CHOICES = [
        ('wall_of_love', 'Wall of Love'),
        ('widgets', 'Widgets'),
        ('pop_ups', 'Pop-ups'),
        ('images', 'Images'),
        ('videos', 'Videos'),
        ('video_embeds', 'Video Embeds'),
    ]

    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='templates/')
    variables = models.JSONField()
    multiple = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Display(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    variables = models.JSONField()
    testimonials = models.ManyToManyField(Testimonial, related_name='displays')
    branding = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='displays/', null=True, blank=True)
    custom_subdomain = models.CharField(max_length=255, blank=True, default='')

    def save(self, *args, **kwargs):

        # Check if the Display is being created
        if not Display.objects.filter(pk=self.id).exists():
            self.variables = self.template.variables['variables']
            super().save(*args, **kwargs)
            return

        # Fetch the original instance from the database
        original = Display.objects.get(pk=self.id)

        # Check if variables or testimonials have changed
        variables_changed = self.variables != original.variables
        testimonials_changed = set(self.testimonials.all()) != set(
            original.testimonials.all())
        print(variables_changed)
        print(testimonials_changed)
        print(self.image)
        super().save(*args, **kwargs)
        if variables_changed or testimonials_changed or self.image == None or self.image == '':

            print('taking new screenshot')
            image = take_screenshot(
                'https://app.99testimonials.com/display/'+str(self.id), self.template)
            if image:
                # Convert the PIL image to a format suitable for ImageField
                image_io = io.BytesIO()
                image.save(image_io, format='PNG')
                image_file = InMemoryUploadedFile(
                    image_io, None, f'{self.id}.png', 'image/png', image_io.tell, None)
                self.image.save(f'{self.id}.png', image_file, save=False)
            else:
                self.image = self.template.image
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
