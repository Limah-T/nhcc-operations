from django.utils import timezone
from django.http.request import HttpRequest
from django.db import transaction, DatabaseError
from nhcc_operations.services.generic_service import (
    server_error, queue_error, diesel_404, 
    no_changes, date_constructor
)
from account.services.profile_service import getFullName
from decimal import Decimal
from ..models import Diesel

class DieselPayloadParser:
    def __init__(self, request:HttpRequest):
        self.request = request

    def parse_single(self) -> dict:
        return {
            "litres": self.request.POST.get("litres"),
            "price": self.request.POST.get("price"),
            "supplier_name": self.request.POST.get("supplier_name"),
            "transport": self.request.POST.get("transport"),
            "date": self.request.POST.get("date")
        }

    def parse_bulk(self) -> dict:
        return {
            "litres": self.request.POST.getlist("litres"),
            "price": self.request.POST.getlist("price"),
            "supplier_name": self.request.POST.getlist("supplier_name"),
            "transport": self.request.POST.getlist("transport"),
            "date": self.request.POST.getlist("date")
        }

class DieselDataRetrieval:

    @staticmethod
    def retrieve_one(id) -> Diesel | None:
        return Diesel.objects.filter(id=id).first()

    @staticmethod
    def retrieve_all() -> Diesel:
        Diesel.objects.all().order_by('-created_at')

    @staticmethod
    def retrieve_bulk(ids) -> Diesel:
        return Diesel.objects.filter(id__in=ids)

    @staticmethod
    def retrieve_by_month(start_date=None, end_date=None) -> Diesel:
        if start_date and end_date:
            return Diesel.objects.filter(
                created_at__gte=start_date,
                created_at__lt=end_date
            ).order_by('-created_at')
                
        now = timezone.now()
        start_date, end_date = date_constructor(now.year, now.month)
        return Diesel.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).order_by('-created_at')


class DieselRecordCalculator:
    def __init__(self):
        self.current_month = timezone.now().month
        self.current_year = timezone.now().year

    def count_monthly_records(
            self, start_date=None, end_date=None)-> int:
        if start_date and end_date:
            return Diesel.objects.filter(
                created_at__gte=start_date,
                created_at__lt=end_date
            ).count()
        
        now = timezone.now()
        start_date, end_date = date_constructor(now.year, now.month)
        return Diesel.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).count()

    def total_monthly_records(
            self, queryset:Diesel, year:int=None, month:int=None
            ) -> Decimal:
        if year and month:
            return sum(
                item.total for item in queryset 
                if item.created_at and (
                        item.created_at.month == month and
                        item.created_at.year == year
                    )
            )
        return sum(
            item.total for item in queryset 
            if item.created_at and (
                    item.created_at.month == self.current_month and
                    item.created_at.year == self.current_year
            ))
            
    def total_annual_records(
            self, queryset:Diesel, year:int=None) -> Decimal:
        if year:
            return sum(
                item.total for item in queryset
                if item.created_at and (
                    (item.created_at.year == year)
            ))
        return sum(
            item.total for item in queryset
            if item.created_at and (
                (item.created_at.year == self.current_year)
        ))

def diesel_context_data(user) -> dict:
    queryset = DieselDataRetrieval().retrieve_by_month()
    total = DieselRecordCalculator().total_monthly_records(queryset)
    return {
        "diesel_records": queryset,
        "count": queryset.count(),
        "monthly_total_display": f"₦{total:,.2f}",
        "user_name":getFullName(user)
    }

class DieselDataInserter:
    def __init__(self, data:list[dict] | dict, user):
        
        self.data = data
        self.user = user
        self.full_name = getFullName(user)

    def insert_one(self):
        transport = self.data.get("transport")
        transport_value = transport if transport else Decimal(0)
        amount = self.data["litres"]*self.data["price"]
        total = amount + transport_value
        Diesel.objects.create(
            litres=self.data["litres"],
            price=self.data["price"],
            amount=amount,
            transport=transport_value,
            supplier_name=self.data["supplier_name"],
            total=total,
            month=timezone.now().strftime("%B"),
            created_at=self.data["date"],
            created_by_user=self.user,
            created_by=self.full_name,
        )
        
    def insert_many(self) -> None:
        diesel_list = []
        for diesel in self.data:
            amount = diesel["litres"]*diesel["price"]
            total = amount + diesel["transport"]
            diesel_list.append(
                Diesel(
                    litres=diesel["litres"],
                    price=diesel["price"],
                    amount=amount,
                    transport=diesel["transport"],
                    supplier_name=diesel["supplier_name"],
                    total=total,
                    month=timezone.now().strftime("%B"),
                    created_at=diesel["date"],
                    created_by_user=self.user,
                    created_by=self.full_name,
            ))
        Diesel.objects.bulk_create(diesel_list)

class DieselDataUpdater:

    @staticmethod
    def can_update(diesel:Diesel, data:dict) -> bool:
        for key,value in data.items():
            if key == "date":
                if diesel.created_at != value:
                    return True
            else:
                if getattr(diesel, key) != value:
                    return True
        return False

    @staticmethod
    def update_one(diesel_id, data:dict, user) -> None:
        amount = data["litres"]*data["price"]
        total = amount + data["transport"]
        Diesel.objects.filter(
            id=diesel_id
            ).update(
                litres=data["litres"],
                price=data["price"],
                amount=amount,
                transport=data["transport"],
                supplier_name=data["supplier_name"],
                total=total,
                created_at=data["date"],
                updated_at=timezone.now().date(),
                updated_by_user=user,
                updated_by=getFullName(user)
            )

class DieselDataDeleter:

    @staticmethod
    def delete_one(id) -> None:
        Diesel.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    @staticmethod
    def delete_many(diesel:Diesel) -> None:
        diesel.delete()

"""################# HELPER FUNCTIONS ##############"""

def create_single(data:dict, user) -> tuple[str, int] | None:
    try:
        DieselDataInserter(data, user).insert_one()
    except Exception:
        return (server_error, 500)
    return None

def create_bulk(data:list[dict], user) -> tuple[str, int] | None:
    try:
        DieselDataInserter(data, user).insert_many()
    except Exception:
        return (server_error, 500)
    return None

def update_single(id, data:dict, user) -> tuple[str, int] | None:
    try:
        diesel = DieselDataRetrieval().retrieve_one(id)
        if diesel is None:
            return (diesel_404, 404)
        updater = DieselDataUpdater()
        if not updater.can_update(diesel, data):
            return (no_changes, 400)
        with transaction.atomic():
            updater.update_one(diesel.id, data, user)
    except Exception:
        return (server_error, 500)
    return None

def delete_single(diesel_id) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            DieselDataDeleter().delete_one(diesel_id)
    except Diesel.DoesNotExist:
        return (diesel_404, 404)
    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None

def delete_bulk(diesel_ids) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            diesel = DieselDataRetrieval(
                ).retrieve_bulk(diesel_ids)
            if not diesel.exists():
                return (diesel_404, 404)
            DieselDataDeleter().delete_many(diesel)
    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None
