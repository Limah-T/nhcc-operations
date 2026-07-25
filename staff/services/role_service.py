from ..models import Role
from django.db import transaction, DatabaseError, IntegrityError
from django.utils import timezone
from django.http.request import HttpRequest
from django.db import transaction, DatabaseError
from nhcc_operations.services.generic_service import (
    server_error, queue_error, role_404, no_changes
)
from account.services.profile_service import getFullName
from ..models import Role

class RolePayloadParser:
    def __init__(self, request:HttpRequest):
        self.request = request

    def parse_single(self) -> dict:
        return {
            "name": self.request.POST.get("name")
        }

    def parse_bulk(self) -> dict:
        return {
            "name": self.request.POST.getlist("name")
        }

class RoleDataRetrieval:

    @staticmethod
    def retrieve_one(id) -> Role | None:
        return Role.objects.filter(id=id).first()

    @staticmethod
    def retrieve_all() -> Role:
        return Role.objects.all().order_by('-created_at')

    @staticmethod
    def retrieve_bulk(ids) -> Role:
        return Role.objects.filter(id__in=ids)


def roleCalculator()-> int:
    return Role.objects.all().count()


class RoleDataInserter:
    def __init__(self, data:list[dict] | dict, user):
        
        self.data = data
        self.user = user
        self.full_name = getFullName(user)
        self.date = timezone.now().date()

    def insert_one(self):
        Role.objects.create(
            name=self.data["name"],
            created_at=self.date,
            created_by_user=self.user,
            created_by=self.full_name
        )
        
    def insert_many(self) -> None:
        role_list = []
        for role in self.data:
            role_list.append(
                Role(
                    name=role["name"],
                    created_at=self.date,
                    created_by_user=self.user,
                    created_by=self.full_name,
            ))
        Role.objects.bulk_create(role_list)

class RoleDataUpdater:

    @staticmethod
    def can_update(role:Role, data:dict) -> bool:
        for key,value in data.items():
            if key == "date":
                if role.created_at != value:
                    return True
            else:
                if getattr(role, key) != value:
                    return True
        return False

    @staticmethod
    def update_one(role_id, data:dict, user) -> None:
        Role.objects.filter(
            id=role_id
            ).update(
                name=data["name"],
                updated_at=timezone.now().date(),
                updated_by_user=user,
                updated_by=getFullName(user)
            )

class RoleDataDeleter:

    @staticmethod
    def delete_one(id) -> None:
        Role.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    @staticmethod
    def delete_many(role:Role) -> None:
        role.delete()

"""################# HELPER FUNCTIONS ##############"""

def create_single(data:dict, user) -> tuple[str, int] | None:
    try:
        RoleDataInserter(data, user).insert_one()
    except IntegrityError:
        return ("Role already exists.", 400)
    except Exception:
        return (server_error, 500)
    return None

def create_bulk(data:list[dict], user) -> tuple[str, int] | None:
    try:
        RoleDataInserter(data, user).insert_many()
    except IntegrityError:
        return ("Role already exists.", 400)
    except Exception:
        return (server_error, 500)
    return None

def update_single(id, data:dict, user) -> tuple[str, int] | None:
    try:
        role = RoleDataRetrieval().retrieve_one(id)
        if role is None:
            return (role_404, 404)
        updater = RoleDataUpdater()
        if not updater.can_update(role, data):
            return (no_changes, 400)
        with transaction.atomic():
            updater.update_one(role.id, data, user)
    except IntegrityError:
        return ("Role already exists.", 400)
    except Exception:
        return (server_error, 500)
    return None

def delete_single(role_id) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            RoleDataDeleter().delete_one(role_id)
    except Role.DoesNotExist:
        return (role_404, 404)
    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None

def delete_bulk(role_ids) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            roles = RoleDataRetrieval(
                ).retrieve_bulk(role_ids)
            if not roles.exists():
                return (role_404, 404)
            RoleDataDeleter().delete_many(roles)
    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None
