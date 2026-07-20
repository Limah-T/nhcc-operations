from django import forms
from .services.report_service import format

class DateForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()




