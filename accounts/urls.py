from django.urls import path
from .views import UserRegistrationView, UserDetailsView, GoogleLoginView, GoogleLogin, ForgotPasswordView, ResetPasswordView, UserEmailLoginView, UserStatsView, ActivateAccountView, ResendActivationEmailView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('details/', UserDetailsView.as_view(), name='user-details'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('login/', UserEmailLoginView.as_view(), name='user-login'),
    path('stats/', UserStatsView.as_view(), name='user-stats'),
    path('activate/<uidb64>/<token>/',
         ActivateAccountView.as_view(), name='activate'),
    path('resend-activation-email/', ResendActivationEmailView.as_view(),
         name='resend-activation-email'),
]

urlpatterns += [
    path('google/', GoogleLogin.as_view(), name='google_login'),
]
