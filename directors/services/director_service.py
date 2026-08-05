from django.utils import timezone
from django.http.request import HttpRequest
from django_countries import countries
from django.db import transaction, DatabaseError, IntegrityError
from core.utils.custom_exceptions import NothingToUpdateError
from core.models import Title
from account.services.profile_service import getFullName
from .position_service import PositionDataRetrieval
from ..models import Director

class DirectorPayloadParser:
    def __init__(self, request:HttpRequest):
        self.request = request

    def parse_single(self) -> dict:
        return {
            "first_name": self.request.POST.get("first_name"),
            "last_name": self.request.POST.get("last_name"),
            "email": self.request.POST.get("email"),
            "phone_number": self.request.POST.get("phone_number"),
            "title": self.request.POST.get("title"),
            "position": self.request.POST.get("position"),
            "nationality": self.request.POST.get("nationality"),
            "date_joined": self.request.POST.get("date_joined")
        }

    def parse_bulk(self) -> dict:
        return {
            "first_name": self.request.POST.getlist("first_name"),
            "last_name": self.request.POST.getlist("last_name"),
            "email": self.request.POST.getlist("email"),
            "phone_number": self.request.POST.getlist("phone_number"),
            "title": self.request.POST.getlist("title"),
            "position": self.request.POST.getlist("position"),
            "nationality": self.request.POST.getlist("nationality"),
            "date_joined": self.request.POST.getlist("date_joined")
        }

class DirectorDataRetrieval:

    @staticmethod
    def retrieve_one(id) -> Director | None:
        return Director.objects.select_related(
            "title", "position"
        ).filter(id=id).first()

    @staticmethod
    def retrieve_all() -> Director:
        return Director.objects.select_related(
            "title", "position"
        ).all().order_by('-created_at')

    @staticmethod
    def retrieve_bulk(ids) -> Director:
        return Director.objects.select_related(
            "title", "position"
        ).filter(id__in=ids)

class DirectorDataCreate:
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
        except IntegrityError:
            raise
        except Exception:
            raise
        return None

    def _insert_one(self):
        Director.objects.create(
            first_name=self.data["first_name"],
            last_name=self.data["last_name"],
            email=self.data["email"],
            phone_number=self.data["phone_number"],
            title=self.data["title"],
            position=self.data["position"],
            nationality=self.data["nationality"],
            date_joined=self.data.get("date_joined", timezone.now().date()),
            created_by_user=self.user,
            created_by=self.full_name,
        )
        
    def _insert_many(self) -> None:
        director_list = []
        for director in self.data:
            director_list.append(
                Director(
                    first_name=director["first_name"],
                    last_name=director["last_name"],
                    email=director["email"],
                    phone_number=director["phone_number"],
                    title=director["title"],
                    position=director["position"],
                    nationality=director["nationality"],
                    date_joined=director.get("date_joined", timezone.now().date()),
                    created_by_user=self.user,
                    created_by=self.full_name,
            ))
        Director.objects.bulk_create(director_list)

class DirectorDataUpdate:
    def __init__(self, data:dict, user):
        self.data = data
        self.user = user

    def update_single(self, id) -> None:
        try:
            director = DirectorDataRetrieval().retrieve_one(id)
            if director is None:
                raise Director.DoesNotExist
            
            if not self._can_update(director):
                raise NothingToUpdateError
            with transaction.atomic():
                self._update_one(director.id)
        except IntegrityError:
            raise
        except Exception:
            raise

    def _can_update(self, director:Director) -> bool:
        for key,value in self.data.items():
            if getattr(director, key) != value:
                return True
        return False

    def _update_one(self, director_id) -> None:
        Director.objects.filter(
            id=director_id
            ).update(
               first_name=self.data["first_name"],
                last_name=self.data["last_name"],
                email=self.data["email"],
                phone_number=self.data["phone_number"],
                title=self.data["title"],
                position=self.data["position"],
                nationality=self.data["nationality"],
                date_joined=self.data["date_joined"],
                updated_at=timezone.now().date(),
            )

class DirectorDataDelete:

    def delete_single(self, director_id) -> None:
        try:
            with transaction.atomic():
                self._delete_one(director_id)
        except Director.DoesNotExist:
            raise
        except DatabaseError:
            raise
        except Exception:
            raise

    def delete_bulk(self, director_ids:list) -> None:
        try:
            with transaction.atomic():
                directors = self._lock_director_list(director_ids)
                if not directors.exists():
                    raise Director.DoesNotExist
                directors.delete()
        except DatabaseError:
            raise
        except Exception:
            raise
        return None

    def _delete_one(self, id) -> None:
        Director.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()
    
    def _lock_director_list(self, director_ids) -> Director:
        return Director.objects.select_for_update(
            nowait=True).filter(
                id__in=director_ids
            )

def director_context_data() -> dict:
    titles = Title.objects.all()
    positions = PositionDataRetrieval().retrieve_all()
    directors = DirectorDataRetrieval().retrieve_all()

    return {
        "countries": countries,
        "directors": directors,
        "titles": titles,
        "positions":positions,
        "total_positions":positions.count(),
        "total_directors":directors.count()
    }

