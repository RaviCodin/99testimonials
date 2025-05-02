from .serializers import CustomerSerializer
from .models import Customer
from rest_framework.decorators import api_view
import json
from rest_framework import viewsets
from .serializers import TagSerializer
from .models import Tag, Customer, TestimonialHighlight
from rest_framework.exceptions import PermissionDenied
import traceback
import random
import string

from testimonials.crawlers.reddit import RedditCrawler
from testimonials.crawlers.instagram2 import InstagramCrawler
from testimonials.crawlers.facebook import FacebookCrawler
from testimonials.crawlers.twitter import TwitterCrawler
from testimonials.crawlers.linkedin import LinkedinCrawler

from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import csv
import requests
from .models import Testimonial, TestimonialImage, TestimonialVideo
from .serializers import TestimonialSerializer, TestimonialImageSerializer, TestimonialVideoSerializer
from projects.models import Project
from django.shortcuts import get_object_or_404


class IsOwnerOrCollaborator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.project.owner or request.user in obj.project.collaborators.all()


class TestimonialPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TestimonialViewSet(viewsets.ModelViewSet):
    serializer_class = TestimonialSerializer
    # permission_classes = [permissions.IsAuthenticated]
    pagination_class = TestimonialPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Testimonial.objects.none()
        project_id = self.kwargs['project_id']
        queryset = Testimonial.objects.filter(project_id=project_id)
        campaign_id = self.request.query_params.get('campaignId', None)
        if campaign_id:
            if campaign_id == 'all':
                queryset = queryset.all()
            elif campaign_id == "import":
                print("fuck")
                queryset = queryset.filter(
                    source='Import').order_by('-created')
            else:
                queryset = queryset.filter(campaignId=campaign_id)
        else:
            queryset = queryset.all()
        return queryset.order_by('-created')

    def perform_create(self, serializer):
        print("fuck me")
        project_id = self.kwargs['project_id']
        print(self.kwargs)
        testimonial = serializer.save(project_id=project_id)
        print(testimonial)
        self.create_or_update_customer(testimonial)

    def create_or_update_customer(self, testimonial):
        print(testimonial)
        project = testimonial.project
        email = testimonial.email
        uid = email if email else ''.join(random.choices(
            string.ascii_letters + string.digits, k=255))
        customer, created = Customer.objects.get_or_create(
            project=project,
            uid=uid,
            defaults={
                'email': email,
                'full_name': testimonial.name,
                'company': testimonial.company,
                'avatar': testimonial.avatar,
                'company_logo': testimonial.company_logo,
            }
        )
        if not created:
            customer.full_name = testimonial.name
            customer.email = email
            customer.company = testimonial.company
            customer.avatar = testimonial.avatar
            customer.save()
        testimonial.customer = customer
        testimonial.save()

    def update(self, request, *args, **kwargs):
        tags = request.data.get('tags')
        if tags:
            tags = json.loads(tags)
            request.data._mutable = True
            request.data.setlist('tags', tags)
            request.data._mutable = False
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        project = serializer.validated_data.get('project')
        if project.owner != self.request.user and self.request.user not in project.collaborators.all():
            return Response({'error': 'You do not have permission to update testimonials for this project.'}, status=status.HTTP_403_FORBIDDEN)
        testimonial = serializer.save()
        self.create_or_update_customer(testimonial)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project = instance.project
        if project.owner != self.request.user and self.request.user not in project.collaborators.all():
            return Response({'error': 'You do not have permission to delete testimonials for this project.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_csv(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        for row in reader:
            testimonial_data = {
                'name': row['name'],
                'tagline': row.get('tagline'),
                'avatar': self.download_media(row.get('avatar')),
                'email': row.get('email'),
                'company': row.get('company'),
                'team': row.get('team'),
                'company_logo': self.download_media(row.get('company_logo')),
                'rating': row['rating'],
                'title': row.get('title'),
                'testimonial': row['testimonial'],
                'url': row.get('url'),
                'project_id': project_id
            }
            tags = row.get('tags', '').split(';')
            serializer = self.get_serializer(data=testimonial_data)
            serializer.is_valid(raise_exception=True)
            testimonial = serializer.save()
            self.create_or_update_customer(testimonial)
            print(tags)
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name, project=project)
                    testimonial.tags.add(tag)

        return Response({'status': 'CSV uploaded successfully'}, status=status.HTTP_201_CREATED)

    def download_media(self, url):
        if url:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
        return None


class SampleCSVView(APIView):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sample_testimonials.csv"'

        writer = csv.writer(response)
        writer.writerow(['name', 'tagline', 'avatar', 'email', 'company',
                        'team', 'company_logo', 'rating', 'title', 'testimonial', 'url', 'tags', 'images', 'videos'])
        writer.writerow(['John Doe', 'CEO', 'http://example.com/avatar.jpg', 'john@example.com', 'Example Inc.', 'Team A',
                        'http://example.com/logo.jpg', '5', 'Great Service', 'This is a testimonial.', 'http://example.com', 'Tag1, Tag2',
                         'http://example.com/image1.jpg,http://example.com/image2.jpg', 'http://example.com/video1.mp4,http://example.com/video2.mp4'])

        return response


class UploadCSVView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        project = Project.objects.get(id=project_id)
        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8-sig')

        try:
            data = json.loads(decoded_file)
        except json.JSONDecodeError:
            return Response({'status': 'Invalid JSON format'}, status=status.HTTP_400_BAD_REQUEST)

        for item in data:
            if not item.get('name') or not item.get('rating') or not item.get('testimonial'):
                continue
            testimonial_data = {
                'name': item.get('name'),
                'tagline': item.get('tagline'),
                'email': item.get('email'),
                'company': item.get('company'),
                'team': item.get('team'),
                'rating': item.get('rating'),
                'title': item.get('title'),
                'testimonial': item.get('testimonial'),
                'url': item.get('url'),
                'project': project_id
            }

            avatar_url = item.get('avatar')
            if avatar_url:
                avatar_file = self.download_media(avatar_url)
                if avatar_file:
                    testimonial_data['avatar'] = avatar_file

            company_logo_url = item.get('company_logo')
            if company_logo_url:
                company_logo_file = self.download_media(company_logo_url)
                if company_logo_file:
                    testimonial_data['company_logo'] = company_logo_file

            serializer = TestimonialSerializer(data=testimonial_data)
            serializer.is_valid(raise_exception=True)
            testimonial = serializer.save()
            self.create_or_update_customer(testimonial, project)

            tags = item.get('tags', '').split(',')
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name, project=project)
                    testimonial.tags.add(tag)

        return Response({'status': 'CSV uploaded successfully'}, status=status.HTTP_201_CREATED)

    def download_media(self, url):
        if url:
            response = requests.get(url)
            if response.status_code == 200:
                from django.core.files.base import ContentFile
                return ContentFile(response.content, name=url.split('/')[-1])
        return None

    def create_or_update_customer(self, testimonial, project):
        email = testimonial.email
        uid = email if email else ''.join(random.choices(
            string.ascii_letters + string.digits, k=255))
        customer, created = Customer.objects.get_or_create(
            project=project,
            uid=uid,
            defaults={
                'email': email,
                'full_name': testimonial.name,
                'company': testimonial.company,
                'avatar': testimonial.avatar
            }
        )
        if not created:
            customer.full_name = testimonial.name
            customer.email = email
            customer.company = testimonial.company
            customer.avatar = testimonial.avatar
            customer.save()
        testimonial.customer = customer
        testimonial.save()


class TestimonialImageViewSet(viewsets.ModelViewSet):
    queryset = TestimonialImage.objects.all()
    serializer_class = TestimonialImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return TestimonialImage.objects.none()
        user = self.request.user
        if user.is_anonymous:
            return TestimonialImage.objects.none()
        return TestimonialImage.objects.filter(testimonial__project__owner=user)

    def perform_create(self, serializer):
        testimonial = serializer.validated_data['testimonial']
        if testimonial.project.owner != self.request.user:
            raise PermissionDenied(
                "You do not have permission to add images to this testimonial.")
        serializer.save()

    def perform_update(self, serializer):
        testimonial = serializer.validated_data['testimonial']
        if testimonial.project.owner != self.request.user:
            raise PermissionDenied(
                "You do not have permission to update images for this testimonial.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.testimonial.project.owner != request.user:
            raise PermissionDenied(
                "You do not have permission to delete images from this testimonial.")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TestimonialVideoViewSet(viewsets.ModelViewSet):
    queryset = TestimonialVideo.objects.all()
    serializer_class = TestimonialVideoSerializer
    permission_classes = []

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return TestimonialVideo.objects.none()
        user = self.request.user
        if user.is_anonymous:
            return TestimonialVideo.objects.none()
        return TestimonialVideo.objects.filter(testimonial__project__owner=user)

    def perform_create(self, serializer):
        testimonial = serializer.validated_data['testimonial']
        serializer.save()

    def perform_update(self, serializer):
        testimonial = serializer.validated_data['testimonial']
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.testimonial.project.owner != request.user:
            raise PermissionDenied(
                "You do not have permission to delete videos from this testimonial.")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImportTestimonialView(APIView):
    def post(self, request, project_id, *args, **kwargs):
        url = request.data.get('url')
        project = get_object_or_404(Project, id=project_id)

        if 'instagram.com' in url:
            crawler = InstagramCrawler()
        elif 'reddit.com' in url:
            crawler = RedditCrawler()
        elif 'facebook.com' in url:
            crawler = FacebookCrawler()
        elif 'linkedin.com' in url:
            crawler = LinkedinCrawler()
        elif 'x.com' or 'twitter.com' in url:
            crawler = TwitterCrawler()
        else:
            return Response({'error': 'Unsupported URL'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            testimonial = crawler.get_info_and_create_testimonial(url, project)
            self.create_or_update_customer(testimonial)
            return Response({'status': 'Testimonial imported successfully', 'testimonial_id': testimonial.id}, status=status.HTTP_201_CREATED)
        except Exception as e:

            print(traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_or_update_customer(self, testimonial):
        project = testimonial.project
        email = testimonial.email
        uid = email if email else ''.join(random.choices(
            string.ascii_letters + string.digits, k=255))
        customer, created = Customer.objects.get_or_create(
            project=project,
            uid=uid,
            defaults={
                'email': email,
                'full_name': testimonial.name,
                'company': testimonial.company,
                'avatar': testimonial.avatar
            }
        )
        if not created:
            customer.full_name = testimonial.name
            customer.email = email
            customer.company = testimonial.company
            customer.team = testimonial.team
            customer.avatar = testimonial.avatar
            customer.save()
        testimonial.customer = customer
        testimonial.save()


class IsProjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.project.owner == request.user


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsProjectOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Tag.objects.none()
        user = self.request.user
        if user.is_anonymous:
            return Tag.objects.none()
        project_id = self.kwargs.get('project_id')
        return Tag.objects.filter(project__owner=user, project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        if project.owner != self.request.user:
            raise PermissionDenied(
                "You do not have permission to add tags to this project.")
        serializer.save(project=project)

    def perform_update(self, serializer):
        project = serializer.instance.project
        if project.owner != self.request.user:
            raise PermissionDenied(
                "You do not have permission to update tags for this project.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.project.owner != request.user:
            raise PermissionDenied(
                "You do not have permission to delete tags from this project.")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_customer(request, customer_id):
    """
    Retrieve a customer by their ID.
    """
    customer = get_object_or_404(Customer, id=customer_id)
    serializer = CustomerSerializer(customer)
    return Response(serializer.data)


@api_view(['GET'])
def get_customer_testimonials(request, customer_id):
    """
    Retrieve all testimonials for a customer by their ID.
    """
    customer = get_object_or_404(Customer, id=customer_id)
    testimonials = Testimonial.objects.filter(customer=customer)
    serializer = TestimonialSerializer(testimonials, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def update_testimonial_highlights(request, testimonial_id):
    """
    Update highlights for a testimonial.
    """
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    highlights_data = request.data.get('highlights', [])

    # Delete existing highlights
    TestimonialHighlight.objects.filter(testimonial=testimonial).delete()

    # Create new highlights
    new_highlights = []
    for highlight in highlights_data:
        new_highlights.append(TestimonialHighlight(
            testimonial=testimonial,
            start_index=highlight['start_index'],
            end_index=highlight['end_index']
        ))

    TestimonialHighlight.objects.bulk_create(new_highlights)

    return Response({"status": "success", "message": "Highlights updated successfully."}, status=status.HTTP_200_OK)
