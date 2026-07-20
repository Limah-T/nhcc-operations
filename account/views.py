from django.shortcuts import render
from .forms import SignupForm, LoginForm, PasswordResetForm
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout

login_temp_name = "account/login.html"
signup_temp_name = "account/signup.html"
reset_temp_name = "account/forgot_password.html"
set_temp_name = "account/new_password.html"
    
class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(
            request, login_temp_name, {"form":form},
            status=200
        )
    
    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.data.get("email")
            password = form.data.get("password")
            user = authenticate(
                request, email=email, 
                password=password
            )
            if user:                
                login(request, user)
                return redirect("dashboard")
            
            form.add_error(
                "email", "No active account with the provided credentials."
            )
            return render(
                request, login_temp_name, {"form":form},
                status=404
            )
        return render(
            request, login_temp_name, {"form":form},
            status=400
        )

class SignUpView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, signup_temp_name, {"form": form})
    
    def post(self, request):
        form = SignupForm(data=request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect("login")
        return render(
            request, signup_temp_name, {"form": form}
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
            return redirect("login")
        
        return render(
            request, set_temp_name, {"form": form}
        )
