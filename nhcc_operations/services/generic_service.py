from datetime import datetime
import calendar, email_validator

def date_constructor(year:int, month:int) -> tuple[datetime.date, datetime.date]:
    _, last_day = calendar.monthrange(year, month)
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, last_day).date()
    return (start_date, end_date)

def email_is_valid(value) -> str | None:
    try:
        email = email_validator.validate_email(
            value, check_deliverability=False
        )
    except email_validator.EmailNotValidError:
        return None
    return email.email.lower()

server_error = "An error occurred, please try again later"
queue_error = "Another device is processing this request."
ekedc_404 = "Electricity record not found."
diesel_404 = "Diesel record not found."
expense_404 = "Expense record not found."
category_404 = "Category record not found."
role_404 = "Role(s) record not found."
staff_404 = "Staff record not found."
no_changes = "Nothing to update"

staff_cred_error = "Email/Phone number/Account number already exists."
empty_fields_error = "All fields are empty"
invalid_name_error = "Only letters, numbers, '.', and ',' are allowed."