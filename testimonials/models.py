import uuid
from django.db import models
from projects.models import Project
from campaigns.models import Campaign
# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=127)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'project')

    def __str__(self):
        return self.name


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, related_name='customers', on_delete=models.CASCADE)
    uid = models.CharField(max_length=255)
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    company_logo = models.ImageField(
        upload_to='company_logos/', blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    avatar = models.ImageField(
        upload_to='customer_avatars/', blank=True, null=True)

    class Meta:
        unique_together = ('project', 'uid')


class Testimonial(models.Model):
    name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    team = models.CharField(max_length=255, blank=True, null=True)
    company_logo = models.ImageField(
        upload_to='company_logos/', blank=True, null=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(0, 6)])
    title = models.CharField(max_length=255, blank=True, null=True)
    testimonial = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    project = models.ForeignKey(
        Project, related_name='testimonials', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='testimonials', blank=True)
    approved = models.BooleanField(default=True)
    source = models.CharField(blank=True, default='Import', max_length=32)
    customer = models.ForeignKey(
        Customer, blank=True, null=True, on_delete=models.SET_NULL)
    campaignId = models.CharField(
        max_length=128, default='', blank=True, null=True,)

    def __str__(self):
        return self.name


class TestimonialHighlight(models.Model):
    testimonial = models.ForeignKey(
        Testimonial, related_name='highlights', on_delete=models.CASCADE)
    start_index = models.IntegerField()
    end_index = models.IntegerField()

    def __str__(self):
        return f"Highlight from {self.start_index} to {self.end_index} in {self.testimonial.name}"


class TestimonialImage(models.Model):
    testimonial = models.ForeignKey(
        Testimonial, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='testimonial_images/')

    def __str__(self):
        return f"Image for {self.testimonial.name}"


class TestimonialVideo(models.Model):
    testimonial = models.ForeignKey(
        Testimonial, related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to='testimonial_videos/')

    def __str__(self):
        return f"Video for {self.testimonial.name}"
