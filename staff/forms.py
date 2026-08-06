from django import forms
from django.utils import timezone
from core.utils.helper_functions import email_is_valid
from core.utils.error_responses import NAME_ERROR
from phonenumber_field.formfields import PhoneNumberField
from .models import Role
import re
    
class RoleForm(forms.Form):
    name = forms.CharField(max_length=25)

    def clean(self):
        name = self.cleaned_data["name"].strip()
        if not re.match(r"^[a-zA-Z0-9\s&,'.-]+$", name):
            raise forms.ValidationError(NAME_ERROR)
        self.cleaned_data["name"] = name.title()
        return self.cleaned_data
    

class StaffForm(forms.Form):
    role = forms.ModelChoiceField(queryset=Role.objects.all())
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(max_length=255)
    phone_number = PhoneNumberField()
    salary = forms.DecimalField(max_digits=15, decimal_places=2)
    bank_name = forms.CharField(max_length=255)
    account_name = forms.CharField(max_length=255)
    account_number = forms.CharField(max_length=50)

    employment_date = forms.DateField(required=False)

    def clean(self):
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        email = self.cleaned_data.get("email")
        bank_name = self.cleaned_data.get("bank_name")
        account_name = self.cleaned_data.get("account_name")
        for value in [first_name, last_name, bank_name, account_name]:
            if not re.match(r"^[a-zA-Z0-9\s&,'.-]+$", value):
                raise forms.ValidationError(NAME_ERROR)
        if email:
            valid_email = email_is_valid(email)
            if not valid_email:
                raise forms.ValidationError("Invalid email")  
        date = self.cleaned_data.get("employment_date")
        if date:
            if date > timezone.now().date():
                raise forms.ValidationError("Date is in the future")
        else:
            self.cleaned_data["employment_date"] = timezone.now().date()
        self.cleaned_data["first_name"] = first_name.title()
        self.cleaned_data["last_name"] = last_name.title()
        self.cleaned_data["email"] = valid_email
        self.cleaned_data["bank_name"] = bank_name.title()
        self.cleaned_data["account_name"] = account_name.title()
        return self.cleaned_data
