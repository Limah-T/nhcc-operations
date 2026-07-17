from django import forms
from decimal import Decimal
import re

class CategoryForm(forms.Form):
    name = forms.CharField(max_length=100, min_length=2)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not re.match(r"^[a-zA-Z0-9\s&,'.-]+$", name):
            raise forms.ValidationError("Invalid name")
        return name.title()          
     

Categoryformset = forms.formset_factory(
            CategoryForm, extra=5
        )       

class DieselForm(forms.Form):
    litres = forms.DecimalField(max_digits=15, decimal_places=2)
    price = forms.DecimalField(max_digits=15, decimal_places=2)
    supplier_name = forms.CharField(max_length=100, min_length=2)
    transport = forms.DecimalField(
        max_digits=15, decimal_places=2, required=False
    )


    def clean_name(self):
        suplier_name = self.cleaned_data.get("supplier_name")
        if not re.match(r"^[a-zA-Z0-9\s&,'.-]+$", suplier_name):
            raise forms.ValidationError("Invalid name")
        return suplier_name.title()          

class ElectricityForm(forms.Form):
    kwh = forms.DecimalField(max_digits=15, decimal_places=2)
    amount = forms.DecimalField(max_digits=15, decimal_places=2)

Categoryformset = forms.formset_factory(
            CategoryForm, extra=5
        ) 
