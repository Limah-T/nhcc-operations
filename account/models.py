from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        self.email = self.email.lower()
        return super().save(*args, **kwargs)

class OtpCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    reset_token = models.CharField(max_length=6, null=True, blank=True)
    verified = models.BooleanField(default=False)
    code_expired_at = models.DateTimeField(null=True, blank=True)
    reset_expired_at = models.DateTimeField(null=True, blank=True)