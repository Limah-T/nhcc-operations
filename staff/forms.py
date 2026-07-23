from django import forms
from django.utils import timezone
from nhcc_operations.services.generic_service import invalid_name_error
from .models import Role
import re
    
class RoleForm(forms.Form):
    name = forms.CharField(max_length=25)

    def clean(self):
        name = self.cleaned_data["name"].replace(" ", "")
        if not re.match(r"^[a-zA-Z0-9\s&,'.-]+$", name):
            raise forms.ValidationError(invalid_name_error)
        self.cleaned_data["name"] = name.title()
        return self.cleaned_data
    
RoleFormset = forms.formset_factory(RoleForm, extra=5)

class StaffForm(forms.Form):
    role = forms.ModelChoiceField(queryset=Role.objects.all())
    full_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)
    salary = forms.DecimalField(max_digits=15, decimal_places=2)
    bank_name = forms.CharField(max_length=255)
    bank_full_name = forms.CharField(max_length=255)
    account_number = forms.CharField(max_length=50)

    employment_date = forms.DateField(required=False)

    def clean(self):
        full_name = self.cleaned_data["full_name"]
        email = self.cleaned_data["email"].replace(" ", "")
        bank_name = self.cleaned_data["bank_name"]
        bank_full_name = self.cleaned_data["bank_full_name"]
        for value in [full_name, bank_name, bank_full_name]:
            if not re.match(r"^[a-zA-Z0-9\s&,'.-]+$", value):
                raise forms.ValidationError(invalid_name_error)
            
        date = self.cleaned_data.get("employment_date")
        if date:
            if date > timezone.now().date():
                raise forms.ValidationError("Date is in the future")
        else:
            self.cleaned_data["employment_date"] = timezone.now().date()
        self.cleaned_data["full_name"] = full_name.title()
        self.cleaned_data["email"] = email.lower()
        self.cleaned_data["bank_name"] = bank_name.title()
        self.cleaned_data["bank_full_name"] = bank_full_name.title()
        return self.cleaned_data

StaffFormset = forms.formset_factory(StaffForm)
