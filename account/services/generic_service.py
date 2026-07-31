from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from nhcc_operations.config.settings.base import env
from ..models import OtpCode, CustomUser
from ..utils.custom_errors import (
    InvalidCredentialsError, TokenError, OtpError
)
import secrets, re

STAFF_ACCOUNTS = set(env("STAFF_EMAILS").split(","))

WELCOME_MESSAGE = "Welcome to NHCC Operations" 
PASSWORD_RESET = "PASSWORD RESET"
RESET_TOKEN_KEY = "reset_token"
EMAIL_EXIST = "An account with this email already exists."
SERVER_ERROR = "Server error, please try again later."
SUCCESSFUL_RESET = "Password reset successfully. Please login to continue."
INVALID_CODE = "Invalid code. Please enter the correct code."
EXPIRED_CODE = "Expired code. Please request a new reset code."
INVALID_TOKEN="Your password reset session is invalid. Please request a new code." 
EXPIRED_TOKEN="Your password reset session has expired. Please request a new code."
WRONG_CREDENTIALS = "No active account with the provided credentials"
INVALID_EMAIL = "Invalid email."
ACCOUNT_DENIED = "You are not allowed to create an account with this email."
NAME_ERROR = "Enter a valid name using letters, spaces, apostrophes, or hyphens only."

NAME_REGEX = r"^[A-Za-z]+(?:[ '-][A-Za-z]+)*$"


def valid_name(value):
    if not re.fullmatch(
        NAME_REGEX,
        value.strip(),
    ):
        return False
    return True

class OtpService:
    def __init__(self):
        self.now = timezone.now()
        self.code_expired_at = 5
        self.reset_expired_at = 10

    def _generate_otp(self) -> int:
        chars = env("otp_chars")
        return "".join(
            secrets.choice(chars)
            for _ in range(6)
        )

    def _generate_reset_token(self) -> str:
        chars = env("reset_token_chars")
        return "".join(
            secrets.choice(chars)
            for _ in range(6)
        )

    def _save_otp(self, user, otp_code, expired_at):
        OtpCode.objects.create(
            user=user,
            otp_code = otp_code,
            code_expired_at = expired_at
        )

    def _save_reset_token(self, obj:OtpCode, reset_token):
        obj.reset_token = reset_token
        obj.reset_expired_at = self.now + timedelta(minutes=self.reset_expired_at)
        obj.save(update_fields=["reset_token", "reset_expired_at"])

    def _update_otp(self, obj:OtpCode):
        obj.verified = True
        obj.save(update_fields=["verified"])

    def get_otp(self, user) -> dict:
        expired_at = timezone.now() + timedelta(minutes=self.code_expired_at)
        otp_code = self._generate_otp()
        self._save_otp(user, otp_code, expired_at)
        return {"otp_code":otp_code, "expired_at":self.code_expired_at}

    def get_token(self, obj) -> str:
        reset_token = self._generate_reset_token()
        self._save_reset_token(obj, reset_token)
        return reset_token

    def _ensure_otp_is_valid(self, otp_code) -> OtpCode | None:
        return OtpCode.objects.select_related("user").filter(
            otp_code=otp_code, code_expired_at__isnull=False
        ).first()

    def _ensure_reset_token_is_valid(self, reset_token)-> OtpCode | None:
        return OtpCode.objects.select_related("user").filter(
            reset_token=reset_token, verified=True,
            reset_expired_at__isnull=False
        ).first()

    def validate_code(self, otp_code)-> OtpCode:
        obj = self._ensure_otp_is_valid(otp_code)
        if obj is None:
            raise OtpError(INVALID_CODE)
        diff = timezone.now() - obj.code_expired_at
        if diff >= timedelta(minutes=self.code_expired_at):
            raise OtpError(EXPIRED_CODE)
        self._update_otp(obj)
        return obj

    def validate_token(self, reset_token) -> CustomUser:
        obj = self._ensure_reset_token_is_valid(reset_token)
        if obj is None:
            raise TokenError(INVALID_TOKEN)
        diff = timezone.now() - obj.reset_expired_at
        if diff >= timedelta(minutes=self.reset_expired_at):
            raise TokenError(EXPIRED_TOKEN)
        if not obj.verified:
            raise TokenError(INVALID_CODE)
        return obj.user

def save_user(data) -> CustomUser:
    with transaction.atomic():
        return CustomUser.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=make_password(data["password"])
      )  

def set_password(user:CustomUser, data:dict) -> None:
    user.set_password(data["new_password"])
    user.save(update_fields=["password"])
    
        
def authenticate_user(request, data:dict) -> CustomUser:
    user = authenticate(
        request, email=data["email"].lower(), 
        password=data["password"]
    )
    if user is None:                
        raise InvalidCredentialsError(WRONG_CREDENTIALS)
    return user

def allow_email(email:str):
    if email not in STAFF_ACCOUNTS:
        raise PermissionDenied(ACCOUNT_DENIED)

def find_user(email) -> CustomUser | None:
    return CustomUser.objects.get(email=email.lower())

# CustomUser.objects.all().delete()
