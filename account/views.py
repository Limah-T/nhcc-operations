from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.conf import settings
from .forms import (
    SignupForm, LoginForm, PasswordResetForm, 
    OtpForm, SetNewPasswordForm
)
from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import login, logout
from .models import CustomUser
from .services.email_service import send_mail
from .services.generic_service import (
    OtpService, set_password, authenticate_user, 
    EMAIL_EXIST, allow_email, save_user, find_user,
    WELCOME_MESSAGE, PASSWORD_RESET, SERVER_ERROR, 
    INVALID_TOKEN, RESET_TOKEN_KEY, SUCCESSFUL_RESET,
    WRONG_CREDENTIALS
)
from .utils.custom_errors import (
    InvalidCredentialsError, TokenError, OtpError
)

login_temp_name = "account/login.html"
signup_temp_name = "account/signup.html"
reset_temp_name = "account/forgot_password.html"
set_temp_name = "account/new_password.html"
otp_display_name = "account/otp_display.html"

acct_created_temp_name = "account/account_created.html"
welcome_temp_name = "account/email_templates/welcome.html"
otp_email_temp_name = "account/email_templates/otp.html"

welcome_text_name = "account/text_templates/welcome.txt"
otp_email_text_name = "account/text_templates/otp.txt"

dashboard_url = "dashboard"
login_url = "login" 

class SignUpView(View):

    def get(self, request):
        form = SignupForm()

        return render(
            request=request, 
            template_name=signup_temp_name, 
            context={"form": form}, status=200
        )        
    
    def post(self, request):
        form = SignupForm(data=request.POST)
        
        if form.is_valid():
            try:
                allow_email(form.cleaned_data["email"])
                user = save_user(form.cleaned_data)
                login_url = request.build_absolute_uri(reverse("login"))
                context = {"user": user, "login_url":login_url}
            except IntegrityError:
                form.add_error("email", EMAIL_EXIST)
            except PermissionDenied as error:
                form.add_error("email", str(error))
            except Exception:
                messages.error(request, SERVER_ERROR)
            else:
                send_mail(
                    WELCOME_MESSAGE, user.email, context, 
                    welcome_temp_name, welcome_text_name
                )
                return render(
                    request=request, 
                    template_name=acct_created_temp_name,
                    context=context, status=200
                )
        return render(
            request=request, 
            template_name=signup_temp_name, 
            context={"form": form}, status=400
        )
             
    
class LoginView(View):
    def get(self, request):

        form = LoginForm()

        return render(
            request=request, 
            template_name=login_temp_name, 
            context={"form":form},
            status=200
        )
        
    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                user = authenticate_user(request, data)
                login(request, user)
                messages.success(request, "Logged In")
                return redirect(dashboard_url)
            except InvalidCredentialsError as error:
                messages.error(request, error)
            except Exception:
                messages.error(request, SERVER_ERROR)

        return render(
            request=request, 
            template_name=login_temp_name, 
            context={"form":form},
            status=400
        )
    
class PasswordResetView(View):
    def get(self, request):
        form = PasswordResetForm()
        return render(request, reset_temp_name, {"form": form})
    
    def post(self, request):
        form = PasswordResetForm(data=request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data["email"]
                user = find_user(email)
                context = OtpService().get_otp(user)
                context.update({"user":user})
                send_mail(
                    PASSWORD_RESET, user.email, 
                    context, otp_email_temp_name, otp_email_text_name
                ) 
                return redirect("otp")  
            except CustomUser.DoesNotExist:
                messages.error(request, WRONG_CREDENTIALS)
            except Exception:
                messages.error(request, SERVER_ERROR)
        
        return render(request, reset_temp_name, {"form": form})
        

class OtpView(View):
    def get(self, request):
        form = OtpForm()
        return render(request, otp_display_name, {"form":form})

    def _set_token_response(self, request, reset_token):
        messages.success(request, "OTP Verified")
        response = redirect("set-password")
        response.set_cookie(
            key=RESET_TOKEN_KEY, value=reset_token,
            httponly=True, secure=settings.HTTP_ONLY_SECURE,         
            samesite="Lax", max_age=600,          
        )
        return response

    def post(self, request):
        form = OtpForm(request.POST)
        if form.is_valid():
            try:
                otp_code = form.cleaned_data["otp_code"]
                service = OtpService()
                obj = service.validate_code(otp_code)
                token = service.get_token(obj)
                return self._set_token_response(request, token) 
            except OtpError as error:
                messages.error(request, error)
            except Exception:
                messages.error(request, SERVER_ERROR)
        return render(request, otp_display_name, {"form":form}) 
                 
class SetNewPasswordView(View):
    def get(self, request):
        form = SetNewPasswordForm()
        return render(request, set_temp_name, {"form": form})

    def _retrieve_reset_token(self, request) -> str:
        reset_token = request.COOKIES.get(RESET_TOKEN_KEY, None)
        if reset_token is None:
            raise TokenError(INVALID_TOKEN)
        return reset_token

    def _delete_reset_token(self, response):
        response.delete_cookie(RESET_TOKEN_KEY)
        return response   

    def post(self, request):
        form = SetNewPasswordForm(data=request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                token = self._retrieve_reset_token(request)
                service = OtpService()
                user = service.validate_token(token)
                set_password(user, data)
            except TokenError as error:
                messages.error(request, error)
            except Exception:
                messages.error(request, SERVER_ERROR)
            else:
                messages.success(request, SUCCESSFUL_RESET)
                response = redirect("login")
                return self._delete_reset_token(response)
        return render(request, set_temp_name, {"form": form})
    
@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "Logged Out!")
    return redirect(login_url)

