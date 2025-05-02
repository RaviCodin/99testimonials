from utils.stats import get_user_stats
from django.utils.http import urlsafe_base64_decode
from django.utils.html import strip_tags
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.shortcuts import render
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from google.oauth2 import id_token
import jwt
import traceback
import requests
from payments.models import PricingPlan
from .serializers import UserRegistrationSerializer, UserDetailsSerializer
from .models import UserDetails
from django.conf import settings

DEFAULT_PAYMENT_PLAN_ID = settings.DEFAULT_PAYMENT_PLAN_ID
BASE_URL = settings.BASE_URL


class UserEmailLoginView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated access

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, created = Token.objects.get_or_create(user=user)
        return Response({"key": token.key})


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated access

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "User with this email already exists."},
                status=status.HTTP_202_ACCEPTED,
            )

        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data["email"])
        user.is_active = False
        user.save()

        # Create UserDetails with default pricing plan
        UserDetails.objects.create(
            user=user,
            gender="M",
            country="Unknown",
            phone="",
            # pricing_plan=PricingPlan.objects.get(id=DEFAULT_PAYMENT_PLAN_ID),
            # pricing_plan=PricingPlan.objects.get(name="Free Plan"),
        )

        # Generate email verification token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(request)
        mail_subject = "Activate your account"
        html_message = render_to_string(
            "accounts/activation_email.html",
            {
                "user": user,
                "domain": BASE_URL,
                "uid": uid,
                "token": token,
            },
        )

        print(
            "domain",
            BASE_URL,
        )
        plain_message = strip_tags(html_message)
        send_mail(
            mail_subject,
            plain_message,
            "noreply@99testimonials.com",
            [email],
            html_message=html_message,
        )

        # Check if the email was sent successfully
        if send_mail:
            return Response(
                {"message": "Please check your email to activate your account."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"error": "Failed to send activation email. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResendActivationEmailView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated access

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not User.objects.filter(email=email).exists():
            return Response(
                {"error": "User with this email doesn't exists."},
                status=status.HTTP_202_ACCEPTED,
            )
        user = User.objects.get(email=email)

        # Generate email verification token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(request)
        mail_subject = "Activate your account"
        html_message = render_to_string(
            "accounts/activation_email.html",
            {
                "user": user,
                "domain": BASE_URL,
                "uid": uid,
                "token": token,
            },
        )
        plain_message = strip_tags(html_message)
        send_mail(
            mail_subject,
            plain_message,
            "noreply@99testimonials.com",
            [user.email],
            html_message=html_message,
        )

        # Check if the email was sent successfully
        if send_mail:
            return Response(
                {
                    "message": "Email sent again! Please check your email to activate your account."
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Failed to send activation email. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserDetailsView(generics.RetrieveUpdateAPIView):
    queryset = UserDetails.objects.all()
    serializer_class = UserDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        user_details, created = UserDetails.objects.get_or_create(
            user=user,
            defaults={
                "gender": "M",
                "country": "Unknown",
                "phone": "",
                "pricing_plan": PricingPlan.objects.get(id=DEFAULT_PAYMENT_PLAN_ID),
                # "pricing_plan": PricingPlan.objects.get(name="Free Plan"),
            },
        )
        return user_details

    def get(self, request, *args, **kwargs):
        user_details = self.get_object()
        serializer = self.get_serializer(user_details)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        user_details = self.get_object()
        serializer = self.get_serializer(user_details, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Update user's first name and last name
        user = user_details.user
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.save()

        return Response(serializer.data)


class GoogleLoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data.get("data", {})
        print(data)
        code = data.get("code")
        print(code)
        if not code:
            return Response(
                {"error": "Authorization code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Exchange the authorization code for tokens
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "code": code,
                "client_id": "433828432142-9737k18j95histlao40juiqcdh4u8afr.apps.googleusercontent.com",
                "client_secret": "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",
                "redirect_uri": "http://localhost:5173",
                "grant_type": "authorization_code",
            }
            token_response = requests.post(token_url, data=token_data)
            token_response_data = token_response.json()
            print(token_response_data)

            if "id_token" not in token_response_data:
                return Response(
                    {"error": "Failed to obtain ID token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            id_token_jwt = token_response_data["id_token"]
            idinfo = jwt.decode(id_token_jwt, options={"verify_signature": False})

            if idinfo["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise ValueError("Wrong issuer.")

            email = idinfo.get("email")
            if not email:
                raise ValueError("Email not available in token")

            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )
            if created:
                user.set_unusable_password()
                user.save()

            token, created = Token.objects.get_or_create(user=user)
            return Response({"key": token.key})

        except ValueError as ve:
            traceback.print_exc()
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()
            return Response(
                {"error": "An error occurred while processing the token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = None  # Define client_class in view


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(request)
        mail_subject = "Reset your password"
        html_message = render_to_string(
            "accounts/forgot_password.html",
            {
                "user": user,
                "domain": BASE_URL,
                "uid": uid,
                "token": token,
            },
        )
        plain_message = strip_tags(html_message)
        send_mail(
            mail_subject,
            plain_message,
            "noreply@99testimonials.com",
            [email],
            html_message=html_message,
        )

        return Response(
            {"message": "Password reset link has been sent to your email"},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print(request.data)
        uidb64 = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("password")

        if not uidb64 or not token or not new_password:
            return Response(
                {"error": "uid, token, and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid uid"}, status=status.HTTP_400_BAD_REQUEST
            )

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password has been reset successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        stats = get_user_stats(user)
        return Response(stats, status=status.HTTP_200_OK)


class ActivateAccountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            token2, created = Token.objects.get_or_create(user=user)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            token, created = Token.objects.get_or_create(
                user=user
            )  # Get or create a new token
            return Response({"key": token.key})
        else:
            return Response(
                {"error": "Activation link is invalid!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
