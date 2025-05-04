from django.contrib.auth.models import User
from django.db import models
from payments.models import PricingPlan


class UserDetails(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="details")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    country = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    display_picture = models.ImageField(
        upload_to="display_pictures/", null=True, blank=True
    )
    pricing_plan = models.ForeignKey(
        PricingPlan, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.country}"
