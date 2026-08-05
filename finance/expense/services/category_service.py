from django.http.request import HttpRequest
from django.db import transaction, IntegrityError, DatabaseError
from core.utils.custom_exceptions import NothingToUpdateError
from account.services.profile_service import getFullName
from ..models import Category

class CategoryPayloadParser:
    def __init__(self, request:HttpRequest):
        self.request = request

    def parse_single(self) -> dict:
        return {"name": self.request.POST.get("name")}

    def parse_bulk(self) -> dict:
        return {"name": self.request.POST.getlist("name")}

class CategoryDataRetrieval:

    @staticmethod
    def retrieve_one(id) -> Category | None:
        return Category.objects.filter(id=id).first()

    @staticmethod
    def retrieve_all() -> Category:
        return Category.objects.all()

    @staticmethod
    def retrieve_bulk(ids) -> Category:
        return Category.objects.filter(id__in=ids)


def category_context_data() -> dict:
    categories = CategoryDataRetrieval().retrieve_all()
    return {
        "categories":categories,
        "count":categories.count(),
    }

class CategoryDataInserter:
    def __init__(self, data:list[dict] | dict, user):
        
        self.data = data
        self.user = user
        self.full_name = getFullName(user)

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
        return None

    def _insert_one(self):
        Category.objects.create(
            name=self.data["name"], 
            created_by_user=self.user,
            created_by=self.full_name
        )
        
    def _insert_many(self) -> None:
        categories = []
        for category in self.data:
            categories.append(
                Category(
                    name=category["name"], 
                    created_by_user=self.user,
                    created_by=self.full_name
            ))
        Category.objects.bulk_create(categories)

class CategoryDataUpdater:
    def __init__(self, data:dict, user):
        self.data = data
        self.user = user

    def update_single(self, id) -> None:
        try:
            category = CategoryDataRetrieval().retrieve_one(id)
            if category is None:
                raise Category.DoesNotExist
            if not self._can_update(category):
                raise NothingToUpdateError
            with transaction.atomic():
               self._update_one(category.id)
        except IntegrityError:
            raise
        except Exception:
            raise

    def _can_update(self, category:Category) -> bool:
        for key,value in self.data.items():
            if getattr(category, key) != value:
                return True
        return False

    def _update_one(self, category_id) -> None:
        Category.objects.select_for_update(
            nowait=True).filter(
            id=category_id).update(
                name=self.data["name"],
                updated_by_user=self.user,
        )

class CategoryDataDeleter:

    def delete_single(self, category_id) -> None:
        try:
            with transaction.atomic():
               self._delete_one(category_id)
        except Category.DoesNotExist:
            raise
        except DatabaseError:
            raise
        except Exception:
            raise

    def delete_bulk(self, category_ids) -> None:
        try:
            with transaction.atomic():
                categories = self._lock_category_list(category_ids)
                if not categories.exists():
                    raise Category.DoesNotExist
                categories.delete()
        except DatabaseError:
            raise
        except Exception:
            raise

    def _delete_one(self, id) -> None:
        Category.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    def _lock_category_list(self, category_ids) -> Category:
        return Category.objects.select_for_update(
            nowait=True).filter(
            id__in=category_ids
    )
