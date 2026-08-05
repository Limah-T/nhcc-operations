from ..models import Role
from django.db import transaction, IntegrityError
from django.db.models import ProtectedError
from django.utils import timezone
from django.http.request import HttpRequest
from core.utils.custom_exceptions import NothingToUpdateError
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

    def create_single(self) -> None:
        try:
            self._insert_one()
        except IntegrityError:
            raise
        except Exception:
            raise

    def create_bulk(self) -> None:
        try:
            self._insert_many()
        except IntegrityError:
            raise
        except Exception:
            raise

    def _insert_one(self):
        Role.objects.create(
            name=self.data["name"],
            created_at=self.date,
            created_by_user=self.user,
            created_by=self.full_name
        )
        
    def _insert_many(self) -> None:
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
    def __init__(self, data:dict, user):
        self.data = data
        self.user = user

    def update_single(self, id) ->  None:
        try:
            role = RoleDataRetrieval().retrieve_one(id)
            if role is None:
                raise Role.DoesNotExist
            if not self._can_update(role):
                raise NothingToUpdateError
            with transaction.atomic():
                self._update_one(role.id)
        except IntegrityError:
            raise
        except Exception:
            raise

    def _can_update(self, role:Role) -> bool:
        for key,value in self.data.items():
            if key == "date":
                if role.created_at != value:
                    return True
            else:
                if getattr(role, key) != value:
                    return True
        return False

    def _update_one(self, role_id) -> None:
        Role.objects.select_for_update(nowait=True).filter(
            id=role_id
            ).update(
                name=self.data["name"],
                updated_at=timezone.now().date(),
                updated_by_user=self.user,
                updated_by=getFullName(self.user)
            )

class RoleDataDeleter:

    def delete_single(self, role_id) -> None:
        try:
            with transaction.atomic():
                self._delete_one(role_id)
        except Role.DoesNotExist:
            raise
        except ProtectedError:
            raise
        except Exception:
            raise

    def delete_bulk(self, role_ids) -> None:
        try:
            with transaction.atomic():
                roles = self._lock_role_list(role_ids)
                if not roles.exists():
                    raise Role.DoesNotExist
                roles.delete()
        except ProtectedError:
            raise
        except Exception:
            raise

    def _delete_one(self, id) -> None:
        Role.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    def _lock_role_list(self, role_ids:list) -> Role:
        return Role.objects.select_for_update(
                nowait=True).filter(
                id__in=role_ids
            )


