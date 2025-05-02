from rest_framework import serializers
from .models import PricingPlan


class PricingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingPlan
        fields = ['id', 'name', 'plan_type', 'amount', 'features', 'active', 'product_id',
                  'testimonials', 'video_testimonials', 'campaigns', 'projects', 'staff', 'recommended']
