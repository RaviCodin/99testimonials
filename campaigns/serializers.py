from rest_framework import serializers
from .models import Campaign
from testimonials.models import Testimonial


class CampaignSerializer(serializers.ModelSerializer):
    testimonials = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = '__all__'

    def get_testimonials(self, obj):
        return Testimonial.objects.filter(campaignId=obj.id).count()
        fields = '__all__'
