from django.db import models

# Create your models here.


class PricingPlan(models.Model):
    PLAN_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=7, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.TextField()
    active = models.BooleanField(default=True)
    recommended = models.BooleanField(default=False)
    product_id = models.CharField(blank=True, max_length=128)
    # limits
    testimonials = models.IntegerField(default=15)
    video_testimonials = models.IntegerField(default=1)
    campaigns = models.IntegerField(default=1)
    projects = models.IntegerField(default=1)
    staff = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name} ({self.plan_type})"


class Transaction(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length=255)
    customer_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    payment_link = models.URLField(max_length=500)

    def __str__(self):
        return f"Transaction {self.subscription_id} for {self.user.username}"
