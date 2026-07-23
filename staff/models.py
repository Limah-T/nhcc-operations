from django.db import models
from account.models import CustomUser

class Role(models.Model):
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="staff_role_created_by_user_id"
    )
    name = models.CharField(max_length=255, unique=True)
    created_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

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

    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, unique=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True, blank=True)
    
    salary = models.DecimalField(max_digits=15, decimal_places=2)
    bonus = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    employment_date = models.DateField()

    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    bank_full_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50, unique=True)
    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)