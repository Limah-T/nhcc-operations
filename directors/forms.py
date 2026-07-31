from django import forms
from core.models import Title
from account.services.generic_service import valid_name, NAME_ERROR
from django_countries.fields import CountryField
from phonenumber_field.formfields import PhoneNumberField
from .models import Position

class PositionForm(forms.Form):
    name = forms.CharField(max_length=255)

    def clean_name(self):
        name = self.cleaned_data["name"]
        if not valid_name(name):
            raise forms.ValidationError(NAME_ERROR)
        return name.title()

class DirectorForm(forms.Form):
    position = forms.ModelChoiceField(queryset=Position.objects.all())
    title = forms.ModelChoiceField(queryset=Title.objects.all())
    nationality = CountryField()
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(max_length=255)
    phone_number = PhoneNumberField()
    date_joined = forms.DateField(input_formats="%Y-%m-%d", required=False)

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




