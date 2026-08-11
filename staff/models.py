from django.db import models
from decimal import Decimal
from phonenumber_field.modelfields import PhoneNumberField
from account.models import CustomUser

class Role(models.Model):
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="staff_role_created_by_user_id"
    )
    updated_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="staff_role_updated_by_user_id"
    )
    name = models.CharField(max_length=255, unique=True)
    created_by = models.CharField(max_length=200)
    created_at = models.DateField(auto_now_add=True)
    updated_by = models.CharField(max_length=200)
    updated_at = models.DateField(auto_now=True)

class Staff(models.Model):
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="staff_created_by_user_id"
    )
    updated_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="staff_updated_by_user_id"
    )
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT,
        null=True, related_name="staff_role"
    )

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, unique=True, null=True)
    phone_number = PhoneNumberField(unique=True)
    
    salary = models.DecimalField(max_digits=15, decimal_places=2)
    bonus = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    employment_date = models.DateField()

    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

class AccountDetail(models.Model):
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="acct_details_created_by_user_id"
    )
    updated_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="acct_details_updated_by_user_id"
    )
    staff = models.OneToOneField(
        Staff,
        on_delete=models.CASCADE,
        related_name="account_detail"
    )
    bank_name = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50, unique=True)
    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

class StaffSalary(models.Model):
    staff = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="staff_salary_created_by_user_id"
    )
    updated_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="staff_salary_updated_by_user_id"
    )
    staff_full_name = models.CharField(max_length=255)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=15)
    amount_deducted = models.DecimalField(
        decimal_places=2, max_digits=15, default=Decimal("0"))
    bonus = models.DecimalField(
        decimal_places=2, max_digits=15, default=Decimal("0")
    )
    additional_info = models.TextField(null=True, blank=True)
    date_received = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
