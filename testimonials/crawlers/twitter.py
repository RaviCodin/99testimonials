import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .crawler import Crawler
from ..models import Testimonial, TestimonialImage, TestimonialVideo, Customer
from twikit.guest import GuestClient
import asyncio


class TwitterCrawler(Crawler):

    async def crawl(self, url, project):

        self.client = GuestClient()
        await self.client.activate()
        tweet_id = url.split('/')[-1]
        tweet = await self.client.get_tweet_by_id(tweet_id)
        return tweet

    def get_info_and_create_testimonial(self, url, project):
        tweet = asyncio.run(self.crawl(url, project))

        # Get or create Customer object
        customer, created = Customer.objects.get_or_create(
            project=project,
            uid=f"{tweet.user.screen_name}@twitter.com",
            defaults={
                'email': "",  # Twitter does not provide email
                'full_name': tweet.user.name,
                'job_title': "",
                'company': "",
                'website_url': ""
            }
        )

        # Create Testimonial object
        testimonial = Testimonial.objects.create(
            name=tweet.user.name,
            email="",  # Twitter does not provide email
            rating=0,  # Assuming a default rating
            testimonial=tweet.text,
            url=url,
            project=project,
            customer=customer  # Set the customer field
        )
        # print(tweet.media)
        # Download and save images/videos
        if tweet.media:
            for media in tweet.media:
                if media['type'] == 'photo':
                    response = requests.get(media['media_url_https'])
                    if response.status_code == 200:
                        image_name = f"{slugify(tweet.user.screen_name)}_{media['id_str']}.jpg"
                        testimonial_image = TestimonialImage(
                            testimonial=testimonial,
                        )
                        testimonial_image.image.save(
                            image_name, ContentFile(response.content))
                        testimonial_image.save()
                elif media['type'] == 'video':
                    video_url = media['video_info']['variants'][0]['url']
                    response = requests.get(video_url)
                    if response.status_code == 200:
                        video_name = f"{slugify(tweet.user.screen_name)}_{media['id_str']}.mp4"
                        testimonial_video = TestimonialVideo(
                            testimonial=testimonial,
                        )
                        testimonial_video.video.save(
                            video_name, ContentFile(response.content))
                        testimonial_video.save()
        return testimonial
