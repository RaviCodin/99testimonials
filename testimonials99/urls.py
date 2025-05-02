"""
URL configuration for testimonials99 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import path, include


from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from dj_rest_auth.registration.views import SocialLoginView
from landing_pages.views import index

schema_view = get_schema_view(
    openapi.Info(
        title="99Testimonials",
        default_version='v1',
        description="API documentation",
    ),

    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],  # Keep this empty if token auth is not required globally
)


urlpatterns = [
    path('admin/', admin.site.urls),

    # for dev purpose, login in browser to test api
    path('api-auth/', include('rest_framework.urls')),
    # auth urls
    # Login, logout, password reset
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/',
         include('dj_rest_auth.registration.urls')),  # Registration
    path('api/accounts/', include('accounts.urls')),  # Add this line

    path('accounts/', include('allauth.urls')),
    # projects
    path('api/projects/', include('projects.urls')),
    # testimonials
    path('api/testimonials/', include('testimonials.urls')),
    # campaigns
    path('api/campaigns/', include('campaigns.urls')),
    # embeds
    path('api/embeds/', include('embeds.urls')),
    # embeds
    path('api/payments/', include('payments.urls')),

    path('api/displays/', include('displays.urls')),

]


urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(
        cache_timeout=0), name='schema-json'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()


urlpatterns += [
    # Catch-all pattern to serve the index.html for any route
    re_path(r'^.*$', index, name='index'),
]
