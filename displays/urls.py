from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_display, name='create_display'),
    path('project/<int:project_id>/displays/',
         views.list_displays_for_project, name='list_displays_for_project'),
    path('update/<uuid:pk>/', views.update_display,
         name='update_display'),
    path('templates/<str:template_type>/',
         views.list_templates_by_type, name='list_templates_by_type'),
    path('templates/',
         views.list_templates, name='list_templates_by_type'),
    path('display/<uuid:pk>/', views.get_display, name='get_display'),
    path('template/<int:pk>/', views.get_template, name='get_template'),
]
