from django.urls import path
from .views import EmbedTemplateListView, EmbedInstanceListCreateView, EmbedInstanceRetrieveUpdateDestroyView, EmbedInstanceDetailView

urlpatterns = [
    path('embed-templates/', EmbedTemplateListView.as_view(),
         name='embed-template-list'),
    path('embed-instances/<int:projectid>/', EmbedInstanceListCreateView.as_view(),
         name='embed-instance-list-create'),
    path('embed-instances/<int:projectid>/<uuid:pk>/',
         EmbedInstanceRetrieveUpdateDestroyView.as_view(), name='embed-instance-detail'),
    path('embed-instance-detail/<uuid:pk>/',
         EmbedInstanceDetailView.as_view(), name='embed-instance-detail-view'),
]
