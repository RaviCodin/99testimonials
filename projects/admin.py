from django.contrib import admin
from .models import Project, Image, Video, BrandLogo, BrandFont, BrandColor

admin.site.register(Project)
admin.site.register(Image)
admin.site.register(Video)
admin.site.register(BrandLogo)
admin.site.register(BrandFont)
admin.site.register(BrandColor)
