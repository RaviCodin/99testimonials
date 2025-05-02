from rest_framework import status
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Campaign
from .serializers import CampaignSerializer
from projects.models import Project


class CampaignPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CampaignPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Campaign.objects.none()
        project_id = self.kwargs['project_id']
        return Campaign.objects.filter(project_id=project_id).order_by('-id')

    def perform_create(self, serializer):
        project_id = self.kwargs['project_id']
        serializer.save(project_id=project_id)

    def perform_update(self, serializer):
        project = serializer.validated_data.get('project')
        if project.owner != self.request.user and self.request.user not in project.collaborators.all():
            return Response({'error': 'You do not have permission to update campaigns for this project.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project = instance.project
        if project.owner != self.request.user and self.request.user not in project.collaborators.all():
            return Response({'error': 'You do not have permission to delete campaigns for this project.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

        from rest_framework import generics


class CampaignDetailView(generics.RetrieveAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    lookup_field = 'id'


class DuplicateCampaignView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        campaign_id = self.kwargs.get('id')
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return Response({'error': 'Campaign not found.'}, status=status.HTTP_404_NOT_FOUND)

        if campaign.project.owner != request.user and request.user not in campaign.project.collaborators.all():
            return Response({'error': 'You do not have permission to duplicate this campaign.'}, status=status.HTTP_403_FORBIDDEN)

        campaign.pk = None  # Reset the primary key to None to create a new instance
        campaign.name = f"{campaign.name} (Copy)"
        campaign.save()

        serializer = CampaignSerializer(campaign)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
