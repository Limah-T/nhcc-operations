class InvalidCredentialsError(Exception):
    pass

class TokenError(Exception):
    pass

class OtpError(Exception):
    pass

EMAIL_EXIST = "An account with this email already exists."
SERVER_ERROR = "Server error, please try again later."
INVALID_CODE = "Invalid code. Please enter the correct code."
EXPIRED_CODE = "Expired code. Please request a new reset code."
INVALID_TOKEN="Your password reset session is invalid. Please request a new code." 
EXPIRED_TOKEN="Your password reset session has expired. Please request a new code."
WRONG_CREDENTIALS = "No active account with the provided credentials"
INVALID_EMAIL = "Invalid email."
ACCOUNT_DENIED = "You are not allowed to create an account with this email."
NAME_ERROR = "Enter a valid name using letters, spaces, apostrophes, or hyphens only."