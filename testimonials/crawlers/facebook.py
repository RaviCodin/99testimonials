import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .crawler import Crawler
from ..models import Testimonial, TestimonialImage, TestimonialVideo


class FacebookCrawler(Crawler):

    def get_info_and_create_testimonial(self, url, project):
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to retrieve the page")

        soup = BeautifulSoup(response.content, 'html.parser')
        print(str(soup)[:1000])
        # Extracting the necessary information
        name = soup.find('meta', property='og:title')['content']
        testimonial_text = soup.find(
            'meta', property='og:description')['content']
        images = soup.find_all('img')
        videos = soup.find_all('video')

        # Create Testimonial object
        testimonial = Testimonial.objects.create(
            name=name,
            email="",  # Facebook does not provide email
            rating=0,  # Assuming a default rating
            testimonial=testimonial_text,
            url=url,
            project=project,
        )

        # Download and save images
        for image in images:
            image_url = image['src']
            response = requests.get(image_url)
            if response.status_code == 200:
                image_name = f"{slugify(name)}_{slugify(image_url)}.jpg"
                testimonial_image = TestimonialImage(
                    testimonial=testimonial,
                )
                testimonial_image.image.save(
                    image_name, ContentFile(response.content))
                testimonial_image.save()

        # Download and save videos
        for video in videos:
            video_url = video['src']
            response = requests.get(video_url)
            if response.status_code == 200:
                video_name = f"{slugify(name)}_{slugify(video_url)}.mp4"
                testimonial_video = TestimonialVideo(
                    testimonial=testimonial,
                )
                testimonial_video.video.save(
                    video_name, ContentFile(response.content))
                testimonial_video.save()

        return testimonial
