from django.db import transaction, IntegrityError, DatabaseError
from django.http.request import HttpRequest
from django.utils import timezone
from core.utils.custom_exceptions import NothingToUpdateError
from account.services.profile_service import getFullName, getNameAvatar
from ..services.account_details_service import (
    AccountDataInserter, AccountDataUpdater
)
from ..services.role_service import RoleDataRetrieval
from ..models import Staff

staff_url_name = "staff"

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
        "total_staff": staff.count(),
        "user_name":getNameAvatar(user)
    }

class StaffDataInserter:
    def __init__(self, data:list[dict] | dict, user):
        
        self.data = data
        self.user = user
        self.full_name = getFullName(user)

    def create_single(self) -> None:
        try:
            with transaction.atomic():
                staff = self._insert_one()
                self.data["staff"] = staff
                AccountDataInserter(self.data, self.user).insert_one()
        except IntegrityError:
            raise
        except Exception:
            raise

    def create_bulk(self) ->  None:
        try:
            with transaction.atomic():
                staff_records = self._insert_many()
                organized_data = staff_organizer(self.data, staff_records)
                AccountDataInserter(organized_data, self.user).insert_many()
        except IntegrityError:
            raise
        except Exception:
            raise

    def _insert_one(self) -> Staff:
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
        
    def _insert_many(self) -> list[Staff]:
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
    def __init__(self, data:dict, user):
        self.data = data
        self.user = user

    def update_single(self, id) -> None:
        try:
            staff = StaffDataRetrieval().retrieve_one(id)
            if staff is None:
                raise Staff.DoesNotExist
            response = self._can_update(staff)
            acct_changes = response["acct_changes"]
            can_update = response["can_update"]
            if not acct_changes and not can_update:
                raise NothingToUpdateError
            with transaction.atomic():
                if can_update:
                    self._update_one(staff.id)
                if acct_changes:
                    AccountDataUpdater().update_one(
                        staff, self.data,self. user
                )
        except IntegrityError:
            raise
        except Exception:
            raise

    def _can_update(self, staff:Staff) -> dict:
        fields = {"bank_name", "account_number", "account_name"}
        
        if self.data["bank_name"] != staff.account_detail.bank_name:
            return {"can_update":True, "acct_changes":True}
        if self.data["account_number"] != staff.account_detail.account_number:
            return {"can_update":True, "acct_changes":True}
        if self.data["account_name"] != staff.account_detail.account_name:
            return {"can_update":True, "acct_changes":True}
        
        for key,value in self.data.items():
            if key not in fields and getattr(staff, key) != value:
                return {"can_update":True, "acct_changes":False}
        return {"can_update":False, "acct_changes":False}

    def _update_one(self, staff_id) -> None:
        Staff.objects.filter(
            id=staff_id
            ).update(
                role=self.data["role"],
                first_name=self.data["first_name"],
                last_name=self.data["last_name"],
                email=self.data["email"],
                phone_number=self.data["phone_number"],
                salary=self.data["salary"],    
                employment_date=self.data["employment_date"],
                updated_at=timezone.now().date(),
                updated_by_user=self.user,
                updated_by=getFullName(self.user)
            )

class StaffDataDeleter:

    def delete_single(self, staff_id) -> None:
        try:
            with transaction.atomic():
                self._delete_one(staff_id)
        except Staff.DoesNotExist:
            raise
        except DatabaseError:
            raise
        except Exception:
            raise

    def delete_bulk(self, staff_ids) ->  None:
        try:
            with transaction.atomic():
                staff = self._lock_staff_list(staff_ids)
                if not staff.exists():
                    raise Staff.DoesNotExist
                staff.delete()
        except DatabaseError:
            raise
        except Exception:
            raise

    def _delete_one(self, id) -> None:
        Staff.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    def _lock_staff_list(self, staff_ids) -> Staff:
        return Staff.objects.select_for_update(
            nowait=True).filter(
            id__in=staff_ids
        )


