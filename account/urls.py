from django.urls import path

from .views import (
    SignUpView, LoginView, 
    PasswordResetView, SetNewPasswordView
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path(
        "forgot/password/", PasswordResetView.as_view(), name="forgot-password"
    ),
    path("set/password/", SetNewPasswordView.as_view(),
        name="set-password")
]