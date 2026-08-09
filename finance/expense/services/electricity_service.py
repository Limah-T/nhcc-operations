from django.utils import timezone
from django.http.request import HttpRequest
from django.db import transaction, DatabaseError
from core.utils.custom_exceptions import NothingToUpdateError
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
    def retrieve_by_month(start_date, end_date) -> EKEDC:
        return EKEDC.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).order_by('created_at')
                
    @staticmethod
    def retrieve_by_year(year:int) -> EKEDC:
        return EKEDC.objects.filter(created_at__year=year)
    

class EkedcRecordCalculator:
 
    @staticmethod
    def total_ekedc_records(queryset:EKEDC) -> Decimal:
        return sum(item.amount for item in queryset)

    @staticmethod
    def total_kwh_records(queryset:EKEDC) -> Decimal:
        return sum(item.kwh for item in queryset)
    

def ekedc_context_data(user, start_date, end_date, form=None) -> dict:
    queryset = EKedcDataRetrieval().retrieve_by_month(start_date, end_date)
    total = EkedcRecordCalculator().total_ekedc_records(queryset)
    return {
        "electricity_records": queryset,
        "count": queryset.count(),
        "monthly_total_display": f"₦{total:,.2f}",
        "user_name":getNameAvatar(user),
        "form": form
    }

class EkedcDataInserter:
    def __init__(self, data:list[dict] | dict, user):
        
        self.data = data
        self.user = user
        self.full_name = getFullName(user)
        self.now = timezone.now()

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

    def _insert_one(self):
        EKEDC.objects.create(
            kwh=self.data["kwh"],
            amount=self.data["amount"],
            month=timezone.now().strftime("%B"),
            created_at=self.data["date"],
            date_recorded=self.now.date(),
            created_by_user=self.user,
            created_by=self.full_name,
        )
        
    def _insert_many(self) -> None:
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
    def __init__(self, data:dict, user):
        self.data = data
        self.user = user

    def update_single(self, id) ->  None:
        try:
            ekedc = EKedcDataRetrieval().retrieve_one(id)
            if ekedc is None:
                raise EKEDC.DoesNotExist
            if not self._can_update(ekedc):
                raise NothingToUpdateError
            with transaction.atomic():
                self._update_one(ekedc.id)
        except DatabaseError:
            raise
        except Exception:
            raise
        return None

    def _can_update(self, ekedc) -> bool:
        for key,value in self.data.items():
            if key == "date":
                if self.ekedc.created_at != value:
                    return True
            else:
                if getattr(ekedc, key) != value:
                    return True
        return False

    def _update_one(self, ekedc_id) -> None:
        EKEDC.objects.select_for_update(nowait=True).filter(
            id=ekedc_id
            ).update(
                kwh=self.data["kwh"],
                amount=self.data["amount"],
                created_at=self.data["date"],
                updated_at=timezone.now().date(),
                updated_by_user=self.user,
                updated_by=getFullName(self.user)
            )

class EkedcDataDeleter:

    def delete_single(self, ekedc_id) -> None:
        try:
            with transaction.atomic():
                self._delete_one(ekedc_id)
        except EKEDC.DoesNotExist:
            raise
        except DatabaseError:
            raise
        except Exception:
            raise

    def delete_bulk(self, ekedc_ids) -> None:
        try:
            with transaction.atomic():
                ekedc = self._lock_ekedc_list(ekedc_ids)
                if not ekedc.exists():
                    raise EKEDC.DoesNotExist
                ekedc.delete()
        except DatabaseError:
            raise
        except Exception:
            raise

    def _delete_one(self, id) -> None:
        EKEDC.objects.select_for_update(
            nowait=True).get(id=id
        ).delete()

    def _lock_ekedc_list(self, ekedc_ids) -> EKEDC:
        return EKEDC.objects.select_for_update(
            nowait=True).filter(
            id__in=ekedc_ids
        )
