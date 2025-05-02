from django.contrib import admin
from .models import PricingPlan, Transaction


class PricingPlanAdmin(admin.ModelAdmin):
    list_filter = ('plan_type',)


# Register your models here.
admin.site.register(PricingPlan, PricingPlanAdmin)
admin.site.register(Transaction)
