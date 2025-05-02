from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CampaignViewSet, CampaignDetailView, DuplicateCampaignView

router = DefaultRouter()
router.register(r'(?P<project_id>\d+)/campaigns',
                CampaignViewSet, basename='campaign')

urlpatterns = router.urls + [
    path('campaigns/<uuid:id>/', CampaignDetailView.as_view(),
         name='campaign-detail'),
    path('campaigns/<uuid:id>/duplicate/',
         DuplicateCampaignView.as_view(), name='campaign-duplicate'),
]
