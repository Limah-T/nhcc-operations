from django.db import models
from account.models import CustomUser

class AccountDetails(models.Model):
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="acct_details_created_by_staff_id"
    )
    updated_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="acct_details_updated_by_staff_id"
    )
    bank_name = models.CharField(max_length=255)
    staff_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Salary(models.Model):
    staff = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="staff_salary"
    )
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="salary_created_by_staff_id"
    )
    updated_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="salary_updated_by_staff_id"
    )
    account_details = models.ForeignKey(
        AccountDetails, on_delete=models.SET_NULL, null=True
    )
    full_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
