from django.urls import path

from .views import (
    SignUpView, LoginView, 
    PasswordResetView, OtpView, 
    SetNewPasswordView, logout_user
)

urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path(
        "forgot/password/", PasswordResetView.as_view(),
        name="forgot-password"
    ),

    path(
        "send/otp-code/", OtpView.as_view(), name="otp"
    ),
    path("set/password/", SetNewPasswordView.as_view(),
        name="set-password"),
        
    path("logout/", logout_user, name="logout")
]