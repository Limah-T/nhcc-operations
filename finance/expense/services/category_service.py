from django.http.request import HttpRequest
from django.db import transaction, IntegrityError, DatabaseError
from nhcc_operations.services.generic_service import (
    server_error, queue_error, category_404, no_changes
)
from account.services.profile_service import getFullName
from ..models import Category

class CategoryPayloadParser:
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

    def insert_one(self):
        Category.objects.create(
            name=self.data["name"], 
            created_by_user=self.user,
            created_by=self.full_name
        )
        
    def insert_many(self) -> None:
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

    @staticmethod
    def can_update(category:Category, data:dict) -> bool:
        for key,value in data.items():
            if getattr(category, key) != value:
                return True
        return False

    @staticmethod
    def update_one(category_id, data:dict, user) -> None:
        Category.objects.filter(
            id=category_id).update(
                name=data["name"],
                updated_by_user=user,
            )

class CategoryDataDeleter:

    @staticmethod
    def delete_one(id) -> None:
        Category.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    @staticmethod
    def delete_many(categories:Category) -> None:
        categories.delete()

"""################# HELPER FUNCTIONS ##############"""

def create_single(data:dict, user) -> tuple[str, int] | None:
    try:
        CategoryDataInserter(data, user).insert_one()
    except Exception:
        return (server_error, 500)
    return None

def create_bulk(data:list[dict], user) -> tuple[str, int] | None:
    try:
        CategoryDataInserter(data, user).insert_many()
    except IntegrityError:
        return ("A few or more category names already exist.", 400)
    except Exception:
        return (server_error, 500)
    return None

def update_single(id, data:dict, user) -> tuple[str, int] | None:
    try:
        category = CategoryDataRetrieval().retrieve_one(id)
        if category is None:
            return (category_404, 404)
        updater = CategoryDataUpdater()
        if not updater.can_update(category, data):
            return (no_changes, 400)
        with transaction.atomic():
            updater.update_one(category.id, data, user)
    except IntegrityError:
        return ("Category name already exist.", 400)
    except Exception:
        return (server_error, 500)
    return None

def delete_single(category_id) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            CategoryDataDeleter().delete_one(category_id)
    except Category.DoesNotExist:
        return (category_404, 404)
    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None

def delete_bulk(category_ids) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            categories = CategoryDataRetrieval(
                ).retrieve_bulk(category_ids)
            if not categories.exists():
                return (category_404, 404)
            CategoryDataDeleter().delete_many(categories)

    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None