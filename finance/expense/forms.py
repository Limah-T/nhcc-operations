from django import forms
from django.utils import timezone
from .models import Category
from decimal import Decimal
import re

class CategoryForm(forms.Form):
    name = forms.CharField(max_length=100, min_length=2)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not re.match(r"^[a-zA-Z0-9\s&,'.-]+$", name):
            raise forms.ValidationError("Invalid name")
        return name.title()          


class DieselForm(forms.Form):
    litres = forms.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)
    price = forms.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)
    supplier_name = forms.CharField(max_length=100, min_length=2)
    transport = forms.DecimalField(
        max_digits=15, decimal_places=2, required=False 
    )
    date = forms.DateField(input_formats=["%Y-%m-%d"], required=False)
    
    def clean_date(self):
        now = timezone.now()
        input_date = self.cleaned_data.get("date")
        if input_date:
            if (input_date.month > now.month or \
                input_date.day > now.day or
                input_date.year > now.year 
            ):
                raise forms.ValidationError("Month or year is in the future.")
        else:
            self.cleaned_data["date"] = now.date()
        return self.cleaned_data["date"]

    def clean_supplier_name(self):
        supplier_name = self.cleaned_data.get("supplier_name")
        if not re.match(r"^[a-zA-Z0-9\s&,'.-]+$", supplier_name):
            raise forms.ValidationError("Invalid name")
        return supplier_name.title()          

class ElectricityForm(forms.Form):
    kwh = forms.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)
    amount = forms.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)
    date = forms.DateField(input_formats=["%Y-%m-%d"], required=False)

    def clean_date(self):
        now = timezone.now()
        input_date = self.cleaned_data.get("date")
        if input_date:
            if (input_date.month > now.month or \
                input_date.day > now.day or
                input_date.year > now.year 
            ):
                raise forms.ValidationError("Month or year is in the future.")
        else:
            self.cleaned_data["date"] = now.date()
        return self.cleaned_data["date"]

class ExpenseForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    name = forms.CharField(max_length=255, min_length=2)
    amount = forms.DecimalField(
        max_digits=15, decimal_places=2, min_value=Decimal("0.01")
    )
    quantity = forms.DecimalField(max_digits=15, decimal_places=2)
    date = forms.DateField(input_formats=["%Y-%m-%d"], required=False)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not re.match(r"^[a-zA-Z0-9\s&,'.-]+$", name):
            raise forms.ValidationError("Invalid name")
        return name.title() 

    def clean_date(self):
        now = timezone.now()
        input_date = self.cleaned_data.get("date")
        if input_date:
            if (input_date.month > now.month or \
                input_date.day > now.day or
                input_date.year > now.year 
            ):
                raise forms.ValidationError("Month or year is in the future.")
        else:
            self.cleaned_data["date"] = now.date()
        return self.cleaned_data["date"]
