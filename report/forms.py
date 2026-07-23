from django import forms
REPORT_TYPES = (
        ("expense", "Expense Report"),
        ("diesel", "Diesel Report"),
        ("electricity", "Electricity Report"),
        ("monthly", "Monthly Expenditure"),
        ("yearly", "Yearly Expenditure"),
    )
class DateForm(forms.Form):
    report_type = forms.ChoiceField(choices=REPORT_TYPES)
    start_date = forms.DateField()
    end_date = forms.DateField()

    




