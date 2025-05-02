from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Project, BrandLogo, BrandColor, BrandFont
from .serializers import ProjectSerializer, ImageSerializer, BrandLogoSerializer, BrandColorSerializer, BrandFontSerializer
from accounts.serializers import UserDetailsSerializer
from rest_framework import status
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from accounts.models import UserDetails
from payments.models import PricingPlan
from django.conf import settings

DEFAULT_PAYMENT_PLAN_ID = settings.DEFAULT_PAYMENT_PLAN_ID


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.owner == request.user or request.user in obj.collaborators.all()
        return obj.owner == request.user


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user) | Project.objects.filter(collaborators=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        if self.get_object().owner != self.request.user:
            raise PermissionDenied(
                "You do not have permission to edit this project.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied(
                "You do not have permission to delete this project.")
        instance.delete()


BASE_URL = settings.BASE_URL


class ManageCollaboratorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, action):
        project = Project.objects.get(pk=pk)

        # Check if the user is the owner or a collaborator
        if project.owner != request.user and request.user not in project.collaborators.all():
            raise PermissionDenied(
                "You do not have permission to modify collaborators for this project.")

        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        try:
            user = User.objects.get(username=email)

            # send email to setup the account
            mail_subject = f"Invitation to collaborate on {project.name}"
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            html_message = render_to_string('accounts/collab_invite_email.html', {
                'user': user,
                'domain': BASE_URL,
                'owner': request.user.first_name + " "+request.user.first_name,
                'project': project.name,
            })
            plain_message = strip_tags(html_message)
            result = send_mail(mail_subject, plain_message, 'noreply@99testimonials.com',
                               [email], html_message=html_message)

        except User.DoesNotExist:
            # Create a new user if the user does not exist
            user = User.objects.create_user(username=email)
            UserDetails.objects.create(
                user=user,
                gender='M',
                country='Unknown',
                phone='',
                pricing_plan=PricingPlan.objects.get(
                    id=DEFAULT_PAYMENT_PLAN_ID)
            )

            # send email to setup the account
            mail_subject = f"Invitation to collaborate on {project.name}"
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            html_message = render_to_string('accounts/collab_invite_email.html', {
                'user': user,
                'domain': BASE_URL,
                'uid': uid,
                'token': token,
                'owner': request.user.first_name + " "+request.user.first_name,
                'project': project.name,
            })
            plain_message = strip_tags(html_message)
            result = send_mail(mail_subject, plain_message, 'noreply@99testimonials.com',
                               [email], html_message=html_message)

        if action == 'add':
            project.collaborators.add(user)
            # Send email

            return Response({"detail": "Collaborator added."})
        elif action == 'remove':
            project.collaborators.remove(user)
            return Response({"detail": "Collaborator removed."})
        else:
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, action):
        project = Project.objects.get(pk=pk)
        owner = project.owner
        collaborators = project.collaborators.all()
        owner_serializer = UserDetailsSerializer(owner.details)
        collaborators_serializer = UserDetailsSerializer(
            [user.details for user in collaborators], many=True)
        return Response({"owner": owner_serializer.data, "collaborators": collaborators_serializer.data})


class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_serializer = ImageSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response({
                "uuid": file_serializer.data['id'],
                "url": file_serializer.data['image']
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BrandLogoViewSet(viewsets.ModelViewSet):
    queryset = BrandLogo.objects.all()
    serializer_class = BrandLogoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BrandLogo.objects.none()
        project_id = self.request.query_params.get('project_id')
        if not project_id:
            raise KeyError("project_id is required as a query parameter.")
        return BrandLogo.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


class BrandColorViewSet(viewsets.ModelViewSet):
    queryset = BrandColor.objects.all()
    serializer_class = BrandColorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BrandColor.objects.none()
        project_id = self.request.query_params.get('project_id')
        if not project_id:
            raise KeyError("project_id is required as a query parameter.")
        return BrandColor.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


class BrandFontViewSet(viewsets.ModelViewSet):
    queryset = BrandFont.objects.all()
    serializer_class = BrandFontSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BrandFont.objects.none()
        project_id = self.request.query_params.get('project_id')
        if not project_id:
            raise KeyError("project_id is required as a query parameter.")
        return BrandFont.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


def perform_destroy(self, instance):
    instance.delete()
