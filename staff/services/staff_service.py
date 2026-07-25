from django.db import transaction, IntegrityError, DatabaseError
from django.http.request import HttpRequest
from django.utils import timezone
from nhcc_operations.services.generic_service import (
    server_error, staff_cred_error, staff_404, no_changes, queue_error
)
from account.services.profile_service import getFullName, getNameAvatar
from ..services.account_details_service import (
    AccountDataInserter, AccountDataUpdater
)
from ..services.role_service import RoleDataRetrieval
from ..models import Staff


staff_url_name = "staff_records"


class StaffPayloadParser:
    def __init__(self, request:HttpRequest):
        self.request = request

    def parse_single(self) -> dict:
        return {
            "role": self.request.POST.get("role"),
            "first_name":self.request.POST.get("first_name"),
            "last_name":self.request.POST.get("last_name"),
            "email":self.request.POST.get("email"),
            "phone_number":self.request.POST.get("phone_number"),
            "salary":self.request.POST.get("salary"),
            "bank_name":self.request.POST.get("bank_name"),
            "account_name":self.request.POST.get("account_name"),
            "account_number":self.request.POST.get("account_number"),
            "employment_date":self.request.POST.get("employment_date")
        }

    def parse_bulk(self) -> dict:
        return {
            "role": self.request.POST.getlist("role"),
            "first_name":self.request.POST.getlist("first_name"),
            "last_name":self.request.POST.getlist("last_name"),
            "email":self.request.POST.getlist("email"),
            "phone_number":self.request.POST.getlist("phone_number"),
            "salary":self.request.POST.getlist("salary"),
            "bank_name":self.request.POST.getlist("bank_name"),
            "account_name":self.request.POST.getlist("account_name"),
            "account_number":self.request.POST.getlist("account_number"),
            "employment_date":self.request.POST.getlist("employment_date")
        }

class StaffDataRetrieval:

    @staticmethod
    def retrieve_one(id) -> Staff | None:
        return Staff.objects.filter(id=id).first()

    @staticmethod
    def retrieve_all() -> Staff:
        return Staff.objects.all().order_by('-first_name')

    @staticmethod
    def retrieve_bulk(ids) -> Staff:
        return Staff.objects.filter(id__in=ids)


def staff_context_data(user) -> dict:
    roles = RoleDataRetrieval().retrieve_all()
    staff = StaffDataRetrieval().retrieve_all()

    return {
        "staff_records": staff,
        "roles":roles,
        "total_roles":roles.count(),
        "user_name":getNameAvatar(user)
    }

class StaffDataInserter:
    def __init__(self, data:list[dict] | dict, user):
        
        self.data = data
        self.user = user
        self.full_name = getFullName(user)

    def insert_one(self) -> Staff:
        return Staff.objects.create(
            role=self.data["role"],
            first_name=self.data["first_name"],
            last_name=self.data["last_name"],
            email=self.data["email"],
            phone_number=self.data["phone_number"],
            salary=self.data["salary"],    
            employment_date=self.data["employment_date"],
            created_by_user=self.user,
            created_by=self.full_name
        )
        
    def insert_many(self) -> list[Staff]:
        staff_list = []
        for staff in self.data:
            staff_list.append(
                Staff(
                    role=staff["role"],
                    first_name=staff["first_name"],
                    last_name=staff["last_name"],
                    email=staff["email"],
                    phone_number=staff["phone_number"],
                    salary=staff["salary"],    
                    employment_date=staff["employment_date"],
                    created_by_user=self.user,
                    created_by=self.full_name
            ))
        return Staff.objects.bulk_create(staff_list)

def staff_organizer(
        data_list:list[dict], staff_records:list[Staff]
    ) -> list[dict]:
    numbers = {staff.phone_number:staff for staff in staff_records}
    new_data = []
    for data in data_list:
        staff = numbers.get(data["phone_number"])
        data["staff"] = staff
        new_data.append(data)

    return new_data

class StaffDataUpdater:

    @staticmethod
    def can_update(staff:Staff, data:dict) -> dict:
        fields = {"bank_name", "account_number", "account_name"}
        
        if data["bank_name"] != staff.account_detail.bank_name:
            return {"can_update":True, "acct_changes":True}
        if data["account_number"] != staff.account_detail.account_number:
            return {"can_update":True, "acct_changes":True}
        if data["account_name"] != staff.account_detail.account_name:
            return {"can_update":True, "acct_changes":True}
        
        for key,value in data.items():
            if key not in fields and getattr(staff, key) != value:
                return {"can_update":True, "acct_changes":False}
        return {"can_update":False, "acct_changes":False}

    @staticmethod
    def update_one(staff_id, data:dict, user) -> None:
        Staff.objects.filter(
            id=staff_id
            ).update(
                role=data["role"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                phone_number=data["phone_number"],
                salary=data["salary"],    
                employment_date=data["employment_date"],
                updated_at=timezone.now().date(),
                updated_by_user=user,
                updated_by=getFullName(user)
            )

class StaffDataDeleter:

    @staticmethod
    def delete_one(id) -> None:
        Staff.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    @staticmethod
    def delete_many(staff:Staff) -> None:
        staff.delete()

"""################# HELPER FUNCTIONS ##############"""

def create_single(data:dict, user) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            staff = StaffDataInserter(data, user).insert_one()
            data["staff"] = staff
            AccountDataInserter(data, user).insert_one()
    except IntegrityError:
        return (staff_cred_error, 400)
    except Exception:
        return (server_error, 500)
    return None

def create_bulk(data:list[dict], user) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            staff_records = StaffDataInserter(data, user).insert_many()
            organized_data = staff_organizer(data, staff_records)
            AccountDataInserter(organized_data, user).insert_many()
    except IntegrityError:
        return (staff_cred_error, 400)
    except Exception:
        return (server_error, 500)
    return None

def update_single(id, data:dict, user) -> tuple[str, int] | None:
    try:
        staff = StaffDataRetrieval().retrieve_one(id)
        if staff is None:
            return (staff_404, 404)
        updater = StaffDataUpdater()
        response = updater.can_update(staff, data)
        acct_changes = response["acct_changes"]
        can_update = response["can_update"]
        if not acct_changes and not can_update:
            return (no_changes, 400)
        with transaction.atomic():
            if can_update:
                updater.update_one(staff.id, data, user)
            if acct_changes:
                AccountDataUpdater().update_one(staff, data, user)
    except IntegrityError:
        return (staff_cred_error, 400)
    except Exception:
        return (server_error, 500)
    return None

def delete_single(staff_id) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            StaffDataDeleter().delete_one(staff_id)
    except Staff.DoesNotExist:
        return (staff_404, 404)
    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None

def delete_bulk(staff_ids) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            staff = StaffDataRetrieval(
                ).retrieve_bulk(staff_ids)
            if not staff.exists():
                return (staff_404, 404)
            StaffDataDeleter().delete_many(staff)
    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None

