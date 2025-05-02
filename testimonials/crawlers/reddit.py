import praw
import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .crawler import Crawler
from ..models import Testimonial, TestimonialImage, TestimonialVideo, Customer


class RedditCrawler(Crawler):

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id="opS3HR2YJIVQT2521GvJTg",
            client_secret="Lafi9-l77fv093VZMWLdwN5OSzhbBQ",
            user_agent="99testimonials",
        )

    def get_info_and_create_testimonial(self, url, project):
        submission = self.reddit.submission(url=url)

        # Get or create Customer object
        customer, created = Customer.objects.get_or_create(
            project=project,
            uid=f"{submission.author.name}@reddit.com",
            defaults={
                'email': "",  # Reddit does not provide email
                'full_name': submission.author.name,
                'job_title': "",
                'company': "",
                'website_url': ""
            }
        )

        # Create Testimonial object
        testimonial = Testimonial.objects.create(
            name=submission.author.name,
            email="",  # Reddit does not provide email
            rating=0,  # Assuming a default rating
            testimonial=submission.selftext,
            url=url,
            project=project,
            source="reddit",
            customer=customer  # Set the customer field
        )

        # Download and save images/videos
        if submission.is_video:
            video_url = submission.media['reddit_video']['fallback_url']
            response = requests.get(video_url)
            if response.status_code == 200:
                video_name = f"{slugify(submission.author.name)}_{submission.id}.mp4"
                testimonial_video = TestimonialVideo(
                    testimonial=testimonial,
                )
                testimonial_video.video.save(
                    video_name, ContentFile(response.content))
                testimonial_video.save()
        elif hasattr(submission, 'preview'):
            for image in submission.preview['images']:
                image_url = image['source']['url']
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_name = f"{slugify(submission.author.name)}_{submission.id}.jpg"
                    testimonial_image = TestimonialImage(
                        testimonial=testimonial,
                    )
                    testimonial_image.image.save(
                        image_name, ContentFile(response.content))
                    testimonial_image.save()
        return testimonial
