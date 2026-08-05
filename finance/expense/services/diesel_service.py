from django.utils import timezone
from django.http.request import HttpRequest
from django.db import transaction, DatabaseError
from core.utils.custom_exceptions import NothingToUpdateError
from account.services.profile_service import getFullName, getNameAvatar
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
    def retrieve_by_month(start_date, end_date) -> Diesel:
        return Diesel.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).order_by('created_at')

    @staticmethod
    def retrieve_by_year(year:int) -> Diesel:
        return Diesel.objects.filter(created_at__year=year)

class DieselRecordCalculator:
        
    @staticmethod
    def total_litre_records(queryset:Diesel) -> Decimal:
        return sum(item.litres for item in queryset)

    @staticmethod
    def total_transport_records(queryset:Diesel) -> Decimal:
        return sum(item.transport for item in queryset)

    @staticmethod
    def total_amount_records(queryset:Diesel) -> Decimal:
        return sum(item.amount for item in queryset)

    @staticmethod
    def total_records(queryset:Diesel) -> Decimal:
        return sum(item.total for item in queryset)
    
def diesel_context_data(user, start_date, end_date) -> dict:
    queryset = DieselDataRetrieval().retrieve_by_month(start_date, end_date)
    total = DieselRecordCalculator().total_records(queryset)
    return {
        "diesel_records": queryset,
        "count": queryset.count(),
        "monthly_total_display": f"₦{total:,.2f}",
        "user_name":getNameAvatar(user)
    }

class DieselDataInserter:
    def __init__(self, data:list[dict] | dict, user):
        
        self.data = data
        self.user = user
        self.full_name = getFullName(user)

    def create_single(self) -> None:
        try:
            self._insert_one()
        except Exception:
            raise

    def create_bulk(self) -> None:
        try:
            self._insert_many()
        except Exception:
            raise

    def _insert_one(self) -> None:
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
            date_recorded=timezone.now().date(),
            created_by_user=self.user,
            created_by=self.full_name,
        )
        
    def _insert_many(self) -> None:
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
                    date_recorded=timezone.now().date,
                    created_by_user=self.user,
                    created_by=self.full_name,
            ))
        Diesel.objects.bulk_create(diesel_list)

class DieselDataUpdater:
    def __init__(self, data:dict, user):
        self.data = data
        self.user = user

    def update_single(self, id) -> None:
        try:
            diesel = DieselDataRetrieval().retrieve_one(id)
            if diesel is None:
                raise Diesel.DoesNotExist
            if not self._can_update(diesel):
                raise NothingToUpdateError
            with transaction.atomic():
                self._update_one(diesel.id)
        except DatabaseError:
            raise
        except Exception:
            raise

    def _can_update(self, diesel:Diesel) -> bool:
        for key,value in self.data.items():
            if key == "date":
                if diesel.created_at != value:
                    return True
            else:
                if getattr(diesel, key) != value:
                    return True
        return False

    def _update_one(self, diesel_id) -> None:
        amount = self.data["litres"]*self.data["price"]
        total = amount + self.data["transport"]
        Diesel.objects.select_for_update(nowait=True).filter(
            id=diesel_id
            ).update(
                litres=self.data["litres"], price=self.data["price"],
                amount=amount, transport=self.data["transport"],
                supplier_name=self.data["supplier_name"],
                total=total, created_at=self.data["date"],
                updated_at=timezone.now().date(),
                updated_by_user=self.user,
                updated_by=getFullName(self.user)
            )

class DieselDataDeleter:

    def delete_single(self, diesel_id) -> None:
        try:
            with transaction.atomic():
                self._delete_one(diesel_id)
        except Diesel.DoesNotExist:
            raise
        except DatabaseError:
            raise
        except Exception:
            raise

    def delete_bulk(self, diesel_ids) -> None:
        try:
            with transaction.atomic():
                diesel = self._lock_diesel_list(diesel_ids)
                if not diesel.exists():
                    raise Diesel.DoesNotExist
                diesel.delete()
        except DatabaseError:
            raise
        except Exception:
            raise

    def _delete_one(self, id) -> None:
        Diesel.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()
    
    def _lock_diesel_list(self, diesel_ids) -> Diesel:
        return Diesel.objects.select_for_update(
            nowait=True).filter(
        id__in=diesel_ids)
