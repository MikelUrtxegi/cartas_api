from django.urls import path
from auth_template.views import (
    LoginView,
    PasswordResetRequestView,
    ResetTokenVerificationView,
    PasswordResetView,
    PasswordResetVerificationView,
    UserView,
    UserDetailView,
)

# General URLs
urls_general = [
    path("login/", LoginView.as_view()),
    path(
        "password_reset_request/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "verify_reset_token/", ResetTokenVerificationView.as_view(), name="verify-token"
    ),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset_verification/",
        PasswordResetVerificationView.as_view(),
        name="password_reset_verification",
    ),
    path("admin/users/", UserView.as_view(), name="users"),
    path("admin/users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]

# Combine all URL patterns
urlpatterns = urls_general
