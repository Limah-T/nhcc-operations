from django import forms
from core.models import Title
from account.services.generic_service import valid_name, NAME_ERROR, INVALID_EMAIL
from django_countries.fields import CountryField
from django.utils import timezone
from phonenumber_field.formfields import PhoneNumberField
from .models import Position
import email_validator

class PositionForm(forms.Form):
    name = forms.CharField(max_length=255)

    def clean_name(self):
        name = self.cleaned_data["name"]
        if not valid_name(name):
            raise forms.ValidationError(NAME_ERROR)
        return name.title()

class DirectorForm(forms.Form):
    first_name = forms.CharField(max_length=255, label="First Name")
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(max_length=255)
    phone_number = PhoneNumberField()
    title = forms.ModelChoiceField(queryset=Title.objects.all())
    position = forms.ModelChoiceField(queryset=Position.objects.all())
    nationality = CountryField().formfield(
        required=True
    )
    date_joined = forms.DateField(required=False)

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

    def clean_email(self):
        try:
            valid_email = email_validator.validate_email(self.cleaned_data["email"])
        except email_validator.EmailNotValidError:
            raise forms.ValidationError(INVALID_EMAIL)
        return valid_email.email.lower()

    def clean_date_joined(self):
        date_joined = self.cleaned_data.get("date_joined")
        date = timezone.now().date()
        if not date_joined:
            date_joined = date
        else:
            if date_joined > date:
                raise forms.ValidationError("Date is in the future")
        return date_joined


