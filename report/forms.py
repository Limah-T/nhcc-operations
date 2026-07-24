from django import forms
from nhcc_operations.services.generic_service import set_date, future_date

REPORT_TYPES = (
        ("expense", "Expense Report"),
        ("diesel", "Diesel Report"),
        ("electricity", "Electricity Report"),
        ("monthly", "Monthly Expenditure"),
        ("yearly", "Yearly Expenditure"),
    )
class ReportForm(forms.Form):
    report_type = forms.ChoiceField(choices=REPORT_TYPES)
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

    def clean(self):
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")
        if start_date and end_date:
            if future_date(start_date, end_date):
                raise forms.ValidationError("Date is in the future.")
        else:
            start_date, end_date = set_date()
            self.cleaned_data["start_date"] = start_date
            self.cleaned_data["end_date"] = end_date 
        return self.cleaned_data         

    






