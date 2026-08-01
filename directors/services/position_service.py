from django.utils import timezone
from django.http.request import HttpRequest
from django.db import transaction, DatabaseError, IntegrityError
from core.utils.custom_exceptions import NothingToUpdateError
from account.services.profile_service import getFullName
from ..models import Position


class PostionPayloadParser:
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

class PositionDataRetrieval:

    @staticmethod
    def retrieve_one(id) -> Position | None:
        return Position.objects.filter(id=id).first()

    @staticmethod
    def retrieve_all() -> Position:
        return Position.objects.all().order_by('-created_at')

    @staticmethod
    def retrieve_bulk(ids) -> Position:
        return Position.objects.filter(id__in=ids)


def positionCounter()-> int:
    return Position.objects.all().count()


class PositionDataCreate:
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
        return 

    def create_bulk(self) -> None:
        try:
            self._insert_many()
        except IntegrityError as e:
            raise
        except Exception:
            raise
        return None

    def _insert_one(self):
        Position.objects.create(
            name=self.data["name"],
            created_at=self.date,
            created_by_user=self.user,
            created_by=self.full_name
        )
        
    def _insert_many(self) -> None:
        position_list = []
        for position in self.data:
            position_list.append(
                Position(
                    name=position["name"],
                    created_at=self.date,
                    created_by_user=self.user,
                    created_by=self.full_name,
            ))
        Position.objects.bulk_create(position_list)

class PositionDataUpdate:
    def __init__(self, data:dict, user):
        self.data = data
        self.user = user

    def update_single(self, id) -> None:
        try:
            position = PositionDataRetrieval().retrieve_one(id)
            if position is None:
                raise Position.DoesNotExist
            
            if not self._can_update(position):
                raise NothingToUpdateError
            with transaction.atomic():
                self._update_one(position.id)
        except IntegrityError:
            raise
        except Exception:
            raise
        return None

    def _can_update(self, position:Position) -> bool:
        for key,value in self.data.items():
            if getattr(position, key) != value:
                return True
        return False

    def _update_one(self, position_id) -> None:
        Position.objects.filter(
            id=position_id
            ).update(
                name=self.data["name"],
                updated_at=timezone.now().date(),
            )

class PositionDataDelete:

    def _delete_one(self, id) -> None:
        Position.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    def _delete_many(self, position:Position) -> None:
        position.delete()

    def delete_single(self, position_id) -> None:
        try:
            with transaction.atomic():
                self._delete_one(position_id)
        except Position.DoesNotExist:
            raise
        except DatabaseError:
            raise
        except Exception:
            raise
        return None

    def delete_bulk(self, position_ids) -> None:
        try:
            with transaction.atomic():
                positions = PositionDataRetrieval(
                    ).retrieve_bulk(position_ids)
                if not positions.exists():
                    raise Position.DoesNotExist
                self._delete_many(positions)
        except DatabaseError:
            raise
        except Exception:
            raise
        return None
