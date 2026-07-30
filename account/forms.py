from django import forms
from .models import CustomUser
from .services.generic_service import NAME_ERROR
import re

NAME_REGEX = r"^[A-Za-z]+(?:[ '-][A-Za-z]+)*$"


def valid_name(value):
    if not re.fullmatch(
        NAME_REGEX,
        value.strip(),
    ):
        return False
    return True

class SignupForm(forms.Form):
    first_name = forms.CharField(min_length=2, max_length=255)
    last_name = forms.CharField(min_length=2, max_length=255)
    email = forms.EmailField(max_length=255)
    password = forms.CharField(min_length=8, max_length=100)

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email"]

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"]
        if not valid_name(first_name):
            raise forms.ValidationError(NAME_ERROR)
        return first_name.title()

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"]
        if not valid_name(last_name):
            raise forms.ValidationError(NAME_ERROR)
        return last_name.title()

    
class LoginForm(forms.Form):
    email = forms.EmailField(max_length=255)
    password = forms.CharField(max_length=255)
    
class PasswordResetForm(forms.Form):
    email = forms.EmailField(max_length=255)

class OtpForm(forms.Form):
    otp_code = forms.CharField(max_length=6)

class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(min_length=8, max_length=100)
    confirm_password = forms.CharField(min_length=8, max_length=100)

    def clean(self):
        data = super().clean()
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
    