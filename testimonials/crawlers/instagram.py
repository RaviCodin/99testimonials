from instagrapi import Client
from .crawler import Crawler
from ..models import Testimonial, TestimonialImage, TestimonialVideo
import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify


class InstagramCrawler(Crawler):

    def __init__(self):
        self.client = Client()

    def get_info_and_create_testimonial(self, url, project):
        media_pk = self.client.media_pk_from_url(url)
        info = self.client.media_info_a1(media_pk=media_pk)

        # Create Testimonial object
        testimonial = Testimonial.objects.create(
            name=info.user.full_name,
            email="",
            rating=0,  # Assuming a default rating
            testimonial=info.caption_text,
            url=url,
            project=project,  # Assuming the user has at least one project
        )

        # Download and save images/videos
        print(info.media_type)
        print(info)

        if info.resources == []:

            if info.media_type == 1:
                response = requests.get(info.thumbnail_url)
                if response.status_code == 200:
                    image_name = f"{slugify(info.user.username)}_{info.pk}.jpg"
                    testimonial_image = TestimonialImage(
                        testimonial=testimonial,
                    )
                    testimonial_image.image.save(
                        image_name, ContentFile(response.content))
                    testimonial_image.save()

            if info.media_type == 2:
                response = requests.get(info.video_url)
                if response.status_code == 200:
                    video_name = f"{slugify(info.user.username)}_{info.pk}.mp4"
                    testimonial_video = TestimonialVideo(
                        testimonial=testimonial,
                    )
                    testimonial_video.video.save(
                        video_name, ContentFile(response.content))
                    testimonial_video.save()

        # resources
        for resource in info.resources:
            if resource.media_type == 1:  # Image
                response = requests.get(resource.thumbnail_url)
                if response.status_code == 200:
                    image_name = f"{slugify(info.user.username)}_{resource.pk}.jpg"
                    testimonial_image = TestimonialImage(
                        testimonial=testimonial,
                    )
                    testimonial_image.image.save(
                        image_name, ContentFile(response.content))
                    testimonial_image.save()
            elif resource.media_type == 2:  # Video
                response = requests.get(resource.video_url)
                print("getting video")

                if response.status_code == 200:
                    video_name = f"{slugify(info.user.username)}_{resource.pk}.mp4"
                    testimonial_video = TestimonialVideo(
                        testimonial=testimonial,
                    )
                    testimonial_video.video.save(
                        video_name, ContentFile(response.content))
                    testimonial_video.save()
        return testimonial
