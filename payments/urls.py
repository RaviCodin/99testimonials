from django.urls import path
from .views import get_active_pricing_plans, subscribe, verify_subscription_status

urlpatterns = [
    path('pricing-plans/', get_active_pricing_plans, name='get_active_pricing_plans'),
    path('subscribe/', subscribe, name='subscribe'),
    path('verify-subscription/<str:subscription_id>/', verify_subscription_status, name='verify_subscription_status'),
]
