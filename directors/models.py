from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from account.models import CustomUser
from core.models import Title

class Position(models.Model):
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=255, unique=True)
    created_by = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

class Director(models.Model):
    position = models.OneToOneField(
        Position, on_delete=models.SET_NULL, null=True, blank=True,
    )
    title = models.ForeignKey(
        Title, on_delete=models.SET_NULL, null=True, blank=True
    ) 
    nationality = CountryField()
    created_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True)
    date_joined = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    created_by = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.title.name}. {self.first_name} {self.last_name}"

