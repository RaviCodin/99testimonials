from django.contrib import admin
from .models import EmbedCategory, EmbedTemplate, EmbedInstance

admin.site.register(EmbedCategory)
admin.site.register(EmbedTemplate)
admin.site.register(EmbedInstance)
