from django.shortcuts import render
from .forms import SignupForm, LoginForm, PasswordResetForm
from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

login_temp_name = "account/login.html"
signup_temp_name = "account/signup.html"
reset_temp_name = "account/forgot_password.html"
set_temp_name = "account/new_password.html"

user_not_found  = "No active account with the provided credentials."
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
            form.save(commit=True)
            return redirect(login_url)
        
        messages.error(request, form.errors)
        return render(
            request=request, 
            template_name=signup_temp_name, 
            context={"form": form},
            status=400
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
            email = form.data.get("email")
            password = form.data.get("password")
            user = authenticate(request, email=email, password=password)
            if user:                
                login(request, user)
                return redirect(dashboard_url)
            else: message, code = user_not_found, 404
        else: message, code = form.errors, 400
        messages.error(request, message)
        return render(
            request=request,  template_name=login_temp_name, 
            context={"form":form}, status=code
        )

    
class PasswordResetView(View):
    def get(self, request):
        form = PasswordResetForm()
        return render(request, reset_temp_name, {"form": form})
    
    def post(self, request):
        form = PasswordResetForm(data=request.POST)
        if form.is_valid():
            return redirect("set-password")
        return render(
            request, reset_temp_name, {"form": form}
        )

class SetNewPasswordView(View):
    def get(self, request):
        form = PasswordResetForm()
        return render(request, set_temp_name, {"form": form})
    
    def post(self, request):
        form = PasswordResetForm(data=request.POST)
        if form.is_valid():
            return redirect(login_url)
        
        return render(
            request, set_temp_name, {"form": form}
        )

@login_required
def logoutUser(request):
    logout(request)
    return redirect(login_url)