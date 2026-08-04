from django.utils import timezone
from django.http.request import HttpRequest
from django.db import transaction, DatabaseError
from nhcc_operations.services.generic_service import (
    server_error, queue_error, ekedc_404, 
    no_changes, date_constructor
)
from account.services.profile_service import getFullName, getNameAvatar
from decimal import Decimal
from ..models import EKEDC

class EkedcPayloadParser:
    def __init__(self, request:HttpRequest):
        self.request = request

    def parse_single(self) -> dict:
        return {
            "kwh": self.request.POST.get("kwh"),
            "amount": self.request.POST.get("amount"),
            "date": self.request.POST.get("date")
        }

    def parse_bulk(self) -> dict:
        return {
            "kwh": self.request.POST.getlist("kwh"),
            "amount": self.request.POST.getlist("amount"),
            "date": self.request.POST.getlist("date")
        }

class EKedcDataRetrieval:

    @staticmethod
    def retrieve_one(id) -> EKEDC | None:
        return EKEDC.objects.filter(id=id).first()

    @staticmethod
    def retrieve_all() -> EKEDC:
        EKEDC.objects.all().order_by('-created_at')

    @staticmethod
    def retrieve_bulk(ids) -> EKEDC:
        return EKEDC.objects.filter(id__in=ids)

    @staticmethod
    def retrieve_by_month(start_date=None, end_date=None) -> EKEDC:
        if start_date and end_date:
            return EKEDC.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).order_by('created_at')
                
        now = timezone.now()
        start_date, end_date = date_constructor(now.year, now.month)
        return EKEDC.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).order_by('created_at')
        

class EkedcRecordCalculator:
    def __init__(self):
        self.current_month = timezone.now().month
        self.current_year = timezone.now().year

    def total_monthly_amount(self, queryset:EKEDC) -> Decimal:
        return sum(item.amount for item in queryset)

    def total_monthly_kwh(self, queryset:EKEDC) -> Decimal:
        return sum(item.kwh for item in queryset)
    
    def total_annual_amount(
            self, queryset:EKEDC, year:int=None) -> Decimal:
        if year:
            return sum(
                item.amount for item in queryset
                if item.created_at and (
                    (item.created_at.year == year)
            ))
        return sum(
            item.amount for item in queryset
            if item.created_at and (
                (item.created_at.year == self.current_year)
        ))

    def total_annual_kwh(
            self, queryset:EKEDC, year:int=None) -> Decimal:
        if year:
            return sum(
                item.kwh for item in queryset
                if item.created_at and (
                    (item.created_at.year == year)
            ))
        return sum(
            item.kwh for item in queryset
            if item.created_at and (
                (item.created_at.year == self.current_year)
        ))

def ekedc_context_data(user, start_date=None, end_date=None) -> dict:
    queryset = EKedcDataRetrieval().retrieve_by_month(start_date, end_date)
    total = EkedcRecordCalculator().total_monthly_amount(queryset)
    return {
        "electricity_records": queryset,
        "count": queryset.count(),
        "monthly_total_display": f"₦{total:,.2f}",
        "user_name":getNameAvatar(user)
    }

class EkedcDataInserter:
    def __init__(self, data:list[dict] | dict, user):
        
        self.data = data
        self.user = user
        self.full_name = getFullName(user)
        self.now = timezone.now()

    def insert_one(self):
        EKEDC.objects.create(
            kwh=self.data["kwh"],
            amount=self.data["amount"],
            month=timezone.now().strftime("%B"),
            created_at=self.data["date"],
            date_recorded=self.now.date(),
            created_by_user=self.user,
            created_by=self.full_name,
        )
        
    def insert_many(self) -> None:
        ekedc_list = []
        for ekedc in self.data:
            ekedc_list.append(
                EKEDC(
                    kwh=ekedc["kwh"],
                    amount=ekedc["amount"],
                    month=timezone.now().strftime("%B"),
                    created_at=ekedc["date"],
                    date_recorded=self.now.date(),
                    created_by_user=self.user,
                    created_by=self.full_name
            ))
        EKEDC.objects.bulk_create(ekedc_list)

class EkedcDataUpdater:

    @staticmethod
    def can_update(ekedc:EKEDC, data:dict) -> bool:
        for key,value in data.items():
            if key == "date":
                if ekedc.created_at != value:
                    return True
            else:
                if getattr(ekedc, key) != value:
                    return True
        return False

    @staticmethod
    def update_one(ekedc_id, data:dict, user) -> None:
        EKEDC.objects.filter(
            id=ekedc_id
            ).update(
                kwh=data["kwh"],
                amount=data["amount"],
                created_at=data["date"],
                updated_at=timezone.now().date(),
                updated_by_user=user,
                updated_by=getFullName(user)
            )

class EkedcDataDeleter:

    @staticmethod
    def delete_one(id) -> None:
        EKEDC.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    @staticmethod
    def delete_many(ekedc:EKEDC) -> None:
        ekedc.delete()

"""################# HELPER FUNCTIONS ##############"""

def create_single(data:dict, user) -> tuple[str, int] | None:
    try:
        EkedcDataInserter(data, user).insert_one()
    except Exception:
        return (server_error, 500)
    return None

def create_bulk(data:list[dict], user) -> tuple[str, int] | None:
    try:
        EkedcDataInserter(data, user).insert_many()
    except Exception:
        return (server_error, 500)
    return None

def update_single(id, data:dict, user) -> tuple[str, int] | None:
    try:
        ekedc = EKedcDataRetrieval().retrieve_one(id)
        if ekedc is None:
            return (ekedc_404, 404)
        updater = EkedcDataUpdater()
        if not updater.can_update(ekedc, data):
            return (no_changes, 400)
        with transaction.atomic():
            updater.update_one(ekedc.id, data, user)
    except Exception:
        return (server_error, 500)
    return None

def delete_single(ekedc_id) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            EkedcDataDeleter().delete_one(ekedc_id)
    except EKEDC.DoesNotExist:
        return (ekedc_404, 404)
    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None

def delete_bulk(ekedc_ids) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            ekedc = EKedcDataRetrieval(
                ).retrieve_bulk(ekedc_ids)
            if not ekedc.exists():
                return (ekedc_404, 404)
            EkedcDataDeleter().delete_many(ekedc)
    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None