from django.db import transaction, IntegrityError, DatabaseError
from django.db.models import Q
from nhcc_operations.services.generic_service import server_error
from ..services.role_service import roleQueryset
from ..services.account_details_service import accountDetailCreator
from ..forms import StaffForm
from ..models import Staff, AccountDetail


url_name = "staff_records"

def staffQueryset() -> Staff:
    return Staff.objects.select_related(
        "role").all().order_by("full_name")

def staffContextData(form=None) -> dict:
    roles = roleQueryset()
    staff = staffQueryset()
    return {
        "staff_records": staff,
        "roles":roles,
        "total_roles":roles.count(),
        "form":form
    }

def staffRetrieval(pk) -> Staff | None:
    return Staff.objects.select_related(
        "account_detail"
    ).filter(id=pk).first()

def staffFormValidator(data:dict) -> StaffForm | list:
    roles = data["roles"]
    full_names = data["full_names"]
    emails = data["emails"]
    phone_numbers = data["phone_numbers"]
    salaries = data["salaries"]
    bank_names = data["bank_names"]
    bank_full_names = data["bank_full_names"]
    account_numbers = data["account_numbers"]
    employment_dates = data["employment_dates"]
    account_list = []
    for role, name, email, number, salary, \
        bank_name, bank_full_name, account_number, date in \
        zip(
            roles, full_names, emails, phone_numbers, 
            salaries, bank_names, bank_full_names,
            account_numbers, employment_dates
    ):
        form = StaffForm(data={
            "role":role,
            "full_name":name,
            "email":email,
            "phone_number":number,
            "salary":salary,
            "bank_name":bank_name,
            "bank_full_name":bank_full_name,
            "account_number":account_number,
            "employment_date":date
        })
        
        if not form.is_valid():
            return form
        account_list.append(form.cleaned_data)
    return account_list

def assignStaffAccount(staff_accounts, details) -> list:
    accounts = {staff.phone_number:staff for staff in staff_accounts}
    for data in details:
        account = accounts.get(data["phone_number"])
        data["staff"] = account
    return details

def staffCreator(staff_data, data:dict) -> list[Staff]:
    staff_list = []
    for details in staff_data:
        staff_list.append(
            Staff(
                created_by_user=data["user"],
                role=details["role"], 
                full_name=details["full_name"],
                email=details["email"],
                phone_number=details["phone_number"],
                salary=details["salary"],
                employment_date=details["employment_date"]
            )
        )

    return Staff.objects.bulk_create(staff_list)

def canUpdate(staff:Staff, validated_data:dict) -> bool:
    
    account_number = validated_data.get(
            "account_number", staff.account_detail.account_number)
    if account_number != staff.account_detail.account_number:
        return True

    for key,value in validated_data.items():
        if key in ["account_number", "bank_full_name", "bank_name"]:
            pass
        else:
            if getattr(staff, key) != value:
                return True
    return False

def duplicateUniqueData(staff:Staff, validated_data:dict) -> bool:
    phone_number = validated_data.get("phone_number", staff.phone_number)
    email = validated_data.get("email", staff.email)
    account_number = validated_data.get(
        "account_number", staff.account_detail.account_number)
    if (
        staff.email != email or\
        staff.phone_number != phone_number or \
        staff.account_detail.account_number != account_number
    ):
        if Staff.objects.filter(
            Q(email=email) | 
            Q(phone_number=phone_number)|
            Q(account_detail__account_number=account_number)
        ).exclude(id=staff.id).exists():
            return True
    return False

def staffUpdater(staff:Staff, validated_data:dict, data:dict) -> None:
    staff.role.name=validated_data["role"].name
    staff.full_name=validated_data["full_name"]
    staff.email=validated_data["email"]
    staff.phone_number=validated_data["phone_number"]
    staff.salary=validated_data["salary"]
    staff.account_detail.bank_name=validated_data["bank_name"]
    staff.account_detail.bank_full_name=validated_data["bank_full_name"]
    staff.account_detail.account_number=validated_data["account_number"]
    staff.employment_date=validated_data["employment_date"]
    staff.updated_by_user=data["user"]
    staff.updated_by=data["user_name"]
    staff.save()
    

def create(staff_data:list, data:dict) -> dict | None:
    try:
        with transaction.atomic():
            new_staff = staffCreator(staff_data, data)
            updated_data = assignStaffAccount(new_staff, staff_data)
            accountDetailCreator(updated_data, data)
    except IntegrityError as e:
        return {"error": "Email/Account/Phone number already exists.", "status":400}
    except Exception:
        return server_error
    return None


def update(staff:Staff, validated_data:dict, user_data:dict) -> dict | None:
    try:
        with transaction.atomic():
            if not canUpdate(staff, validated_data):
                return {"error": "Nothing to update.", "status":400}
            if duplicateUniqueData(staff, validated_data):
                return {
                    "error": "Email/Account/Phone number already exists.", 
                    "status":400
                }
            staffUpdater(staff, validated_data, user_data)
    except IntegrityError:
        return {
            "error": "Email/Account/Phone number already exists.", 
            "status":400
        }
    except Exception:
        return server_error
    return None