from django.shortcuts import render
from dodopayments import DodoPayments
from django.conf import settings

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PricingPlan, Transaction
from .serializers import PricingPlanSerializer


@api_view(["GET"])
def get_active_pricing_plans(request):
    active_plans = PricingPlan.objects.filter(active=True)
    serializer = PricingPlanSerializer(active_plans, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def subscribe(request):
    product_id = request.data.get("product_id")
    if not product_id:
        return Response({"error": "Product ID is required"}, status=400)

    client = DodoPayments(
        bearer_token=settings.DODO_PAYMENTS_API_KEY, environment="test_mode"
    )
    subscription = client.subscriptions.create(
        billing={
            "city": "city",
            "country": "IN",
            "state": "state",
            "street": "street",
            "zipcode": 54535,
        },
        customer={
            "email": request.user.email,
            "name": request.user.username,
        },
        product_id=product_id,
        quantity=1,
        payment_link=True,
        return_url="https://app.99testimonials.com/payment/verify/",
    )
    transaction = Transaction.objects.create(
        user=request.user,
        subscription_id=subscription.subscription_id,
        customer_id=subscription.customer.customer_id,
        client_secret=subscription.client_secret,
        payment_link=subscription.payment_link,
    )
    transaction.save()
    return Response(
        {
            "subscription_id": subscription.subscription_id,
            "payment_link": subscription.payment_link,
        }
    )


@api_view(["GET"])
def verify_subscription_status(request, subscription_id):
    if not subscription_id:
        return Response({"error": "Subscription ID is required"}, status=400)

    client = DodoPayments(
        bearer_token=settings.DODO_PAYMENTS_API_KEY, environment="test_mode"
    )
    try:
        subscription = client.subscriptions.retrieve(subscription_id)
        transaction = Transaction.objects.get(subscription_id=subscription_id)
        print(subscription)
        print(transaction)
        if subscription.status == "active":
            transaction.user.details.pricing_plan = PricingPlan.objects.get(
                product_id=subscription.product_id
            )
            transaction.user.details.save()
        status = subscription.status
        return Response({"subscription_id": subscription_id, "status": status})
    except Exception as e:
        return Response({"error": str(e)}, status=400)
