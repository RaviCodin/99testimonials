from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProjectListCreateView, ProjectRetrieveUpdateDestroyView, ManageCollaboratorView, ImageUploadView, BrandLogoViewSet, BrandColorViewSet, BrandFontViewSet

router = DefaultRouter()

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:pk>/', ProjectRetrieveUpdateDestroyView.as_view(),
         name='project-detail'),
    path('<int:pk>/collaborators/<str:action>/',
         ManageCollaboratorView.as_view(), name='manage-collaborator'),
    path('upload-image/', ImageUploadView.as_view(), name='upload-image'),
]

router.register(r'brand-logos', BrandLogoViewSet, basename='brandlogo')
router.register(r'brand-colors', BrandColorViewSet, basename='brandcolor')
router.register(r'brand-fonts', BrandFontViewSet, basename='brandfont')
urlpatterns += router.urls
