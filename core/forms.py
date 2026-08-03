from django import forms

class DateForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()