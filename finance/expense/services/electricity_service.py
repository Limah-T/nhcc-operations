from django.utils import timezone
from django.db import transaction, IntegrityError, DatabaseError
from nhcc_operations.services.generic_service import (
    server_error, queue_error
)
from ..models import EKEDC
from ..forms import ElectricityForm


def ekedcQuerySet() -> EKEDC:
    return EKEDC.objects.all().order_by('-created_at')

def ekedcRetrieval(pk:int) -> EKEDC | None:
    return EKEDC.objects.filter(id=pk).first()

def totalMonthlyPrepaid(queryset:EKEDC) -> int:
    now = timezone.now()
    return sum(
            item.amount for item in queryset 
                if (
                    item.created_at.year and item.created_at.month
                    ) == (now.year and now.month
                )
        )

def totalAnnualPrepaid(queryset:EKEDC) -> int:
    now = timezone.now()
    return sum(
            item.amount for item in queryset
            if (item.created_at.year == now.year)
    )

def ekedcFormValidator(kwh, amount) -> ElectricityForm:
    return ElectricityForm(
        data={"kwh":kwh, "amount":amount}
    )
    
def prepareCreate(
        kwhs:list, amounts:list, user_id, full_name
    ) -> ElectricityForm | list:
    electricity_list = []
    for kwh, amt in zip(kwhs, amounts):
        amount = amt.replace(",","")
        form = ElectricityForm(
            data={
                "kwh":kwh,
                "amount": amount
            }
        )
        if not form.is_valid():
           return form
        electricity_list.append(
            EKEDC(
                kwh=kwh,
                amount=amount,
                month=timezone.now().strftime("%B"),
                created_by_user_id=user_id,
                created_by=full_name,
            )
        )
    return electricity_list

def nothing_to_update(ekedc, kwh, amount) -> bool:
    if ekedc.kwh == kwh and ekedc.amount == amount:
        return True
    return False

def ekedcCreate(electricity_list:list):
    EKEDC.objects.bulk_create(electricity_list)
    
def ekedcUpdate(
        ekedc:EKEDC, kwh, amount, user_id, full_name
    ) -> None:
    EKEDC.objects.select_for_update(nowait=True
    ).filter(id=ekedc.id
    ).update(
        kwh=kwh, amount=amount,
        updated_by_user_id=user_id,
        updated_by=full_name
    )
    return None

def create(electricity_list:list) -> dict | None:
    try:
        with transaction.atomic():
            ekedcCreate(electricity_list)
    except IntegrityError:
        return server_error
    except Exception:
        return server_error
    return None

def update(
        ekedc:EKEDC, kwh, amount, user_id, full_name
    ) -> dict | None:
    try:
        if nothing_to_update(ekedc, kwh, amount):
            return {"Equality": ["Nothing to update"]}
        with transaction.atomic():
            ekedcUpdate(ekedc, kwh, amount, user_id, full_name)
    except DatabaseError:
        return queue_error
    except Exception:
        return server_error
    return None


def delete_one(ekedc:EKEDC):
    try:
        with transaction.atomic():
            EKEDC.objects.select_for_update(nowait=True).get(
                id=ekedc.id
            ).delete()
    except DatabaseError:
        return queue_error
    except Exception:
        return server_error
    
def delete_many(ekedc:list):
    try:
        with transaction.atomic():
            EKEDC.objects.select_for_update(nowait=True).filter(
                id__in=ekedc
            ).delete()
    except DatabaseError:
        return queue_error
    except Exception:
        return server_error