from django.db import models
from account.models import CustomUser
from decimal import Decimal

class Category(models.Model):
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="category_created_by_staff_id"
    )
    updated_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="category_updated_by_staff_id"
    )
    name = models.CharField(max_length=200, unique=True)
    created_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

class Diesel(models.Model):
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="diesel_created_by_staff_id"
    )
    updated_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="diesel_updated_by_staff_id"
    )
    litres = models.DecimalField(max_digits=15, decimal_places=2)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    total = models.DecimalField(max_digits=15, decimal_places=2)
    month = models.CharField(max_length=30)
    transport = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"))
    supplier_name = models.CharField(max_length=200)
    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EKEDC(models.Model):
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="ekedc_created_by_staff_id"
    )
    updated_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="ekedc_updated_by_staff_id"
    )
    kwh = models.DecimalField(max_digits=15, decimal_places=2)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    month = models.CharField(max_length=30)
    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

class Expense(models.Model):
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="expense_created_by_staff_id"
    )
    updated_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, 
        null=True, related_name="expense_updated_by_staff_id"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True
    )
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0')
    )
    total = models.DecimalField(max_digits=15, decimal_places=2)
    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
