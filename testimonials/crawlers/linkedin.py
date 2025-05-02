import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .crawler import Crawler
from ..models import Testimonial, TestimonialImage, TestimonialVideo, Customer


class LinkedinCrawler(Crawler):

    def get_info_and_create_testimonial(self, url, project):
        response = requests.get(
            f"https://curator.senja.io/linkedin/lookup?urls={url}")
        if response.status_code != 200:
            raise Exception("Failed to fetch LinkedIn post data")

        data = response.json()[0]

        # Get or create Customer object
        customer, created = Customer.objects.get_or_create(
            project=project,
            uid=f"{data.get('customer_name', 'unknown')}@linkedin.com",
            defaults={
                'email': "",  # LinkedIn does not provide email
                'full_name': data.get('customer_name', 'Unknown'),
                'job_title': "",
                'company': "",
                'website_url': ""
            }
        )

        # Create Testimonial object
        testimonial = Testimonial.objects.create(
            name=data.get('customer_name', 'Unknown'),
            email="",  # LinkedIn does not provide email
            rating=0,  # Assuming a default rating
            testimonial=data['content'].get('text', ''),
            url=data['content'].get('url', ''),
            project=project,
            source="linkedin",
            customer=customer  # Set the customer field
        )

        # Download and save images/videos
        if 'media' in data['content']:
            for media in data['content']['media']:
                if media['type'] == 'image':
                    response = requests.get(media['url'])
                    if response.status_code == 200:
                        image_name = f"{slugify(data.get('customer_name', 'unknown'))}_{slugify(data.get('platform_id', 'unknown'))}.jpg"
                        testimonial_image = TestimonialImage(
                            testimonial=testimonial,
                        )
                        testimonial_image.image.save(
                            image_name, ContentFile(response.content))
                        testimonial_image.save()
                elif media['type'] == 'video':
                    response = requests.get(media['url'])
                    if response.status_code == 200:
                        video_name = f"{slugify(data.get('customer_name', 'unknown'))}_{slugify(data.get('platform_id', 'unknown'))}.mp4"
                        testimonial_video = TestimonialVideo(
                            testimonial=testimonial,
                        )
                        testimonial_video.video.save(
                            video_name, ContentFile(response.content))
                        testimonial_video.save()
        return testimonial
