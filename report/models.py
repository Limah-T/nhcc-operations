from django.db import models
from account.models import CustomUser

class Report(models.Model):
    REPORT_TYPES = (
        ("expense", "Expense Report"),
        ("diesel", "Diesel Report"),
        ("electricity", "Electricity Report"),
        ("monthly", "Monthly Expenditure"),
        ("yearly", "Yearly Expenditure"),
    )

    report_type = models.CharField(
        max_length=100, choices=REPORT_TYPES
    )
    file = models.FileField(upload_to="reports/")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, blank=True
    )
    created_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
