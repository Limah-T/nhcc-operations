from django import forms
from .models import CustomUser
from nhcc_operations.config.settings.base import env

staff_accounts = set(env("STAFF_EMAILS").split(","))

class SignupForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=255)
    password = forms.CharField(min_length=8, max_length=100)
    confirm_password = forms.CharField(min_length=8, max_length=100)

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email"]

    def clean_email(self):
        cleaned_email = self.cleaned_data["email"]
        email = " ".join(cleaned_email.split()).lower()
        if email not in staff_accounts:
            raise forms.ValidationError("Permission Denied")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
    
    def save(self, commit=True):
        password = self.cleaned_data["password"]
        user = super().save(commit=False)
        user.set_password(password)
        if commit:
            user.save()
        return user
    
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()

    def clean_email(self):
        cleaned_email = self.cleaned_data["email"]
        email = " ".join(cleaned_email.split()).lower()   
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "No active account with the provided credentials"
            )
        return email
    
class PasswordResetForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        cleaned_email = self.cleaned_data["email"]
        email = " ".join(cleaned_email.split()).lower()   
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "No active account with the provided credentials"
            )
        return email

class SetNewPasswordForm(forms.ModelForm):
    new_password = forms.CharField(min_length=8, max_length=100)
    confirm_password = forms.CharField(min_length=8, max_length=100)

    def clean(self):
        data = super().clean()
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
    