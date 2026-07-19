from django.utils import timezone
from decimal import Decimal
from django.db import transaction, IntegrityError, DatabaseError
from nhcc_operations.services.generic_service import (
    server_error, queue_error
)
from ..models import Diesel
from ..forms import DieselForm

def dieselQueryset() -> Diesel:
    return Diesel.objects.all().order_by('-created_at')

def dieselRetrieval(pk:int) -> Diesel | None:
    return Diesel.objects.filter(id=pk).first()

def totalMonthlyDiesel(queryset:Diesel) -> int:
    now = timezone.now()
    return sum(
        item.total for item in queryset if (
            item.created_at.month and item.created_at.year
        ) == (now.month and now.year)
        )


def totalAnnualDiesel(queryset:Diesel) -> int:
    now = timezone.now()
    return sum(
            item.amount for item in queryset
            if (item.created_at.year == now.year)
    )

def dieselCreate(diesel_list:list[Diesel]) -> None:
    Diesel.objects.bulk_create(diesel_list)  
    return None

def dieselFormValidator(
        supplier_name, litres, price, tfare
    ) -> DieselForm:
    form = DieselForm(
        data={
           "litres":litres, "price":price,
            "supplier_name": supplier_name,
            "transport":tfare        
        }
    )
    return form
    
def dieselUpdate(
        diesel:Diesel, price, litres, 
        tfare, supplier, user, user_name
    ) -> None:
    
    Diesel.objects.filter(
        id=diesel.id).select_for_update(nowait=True
    ).update(
        litres=litres, price=price,
        supplier_name=supplier,
        amount=price*litres,
        total=(price*litres)+tfare,
        transport=tfare,
        updated_by_user=user,
        updated_by=user_name
    )

def prepareCreate(
        supplier_names:list,litres:list, 
        prices:list, transports:list, user_name:str, 
        user_id) -> DieselForm | list[Diesel]:
    diesel_list = []
    for supplier, litre, price, transport in zip(
        supplier_names, litres, prices, transports):
        form = dieselFormValidator(
            supplier, litre, price, transport
        )
        if not form.is_valid():
            return form
        cleaned_litre = form.cleaned_data["litres"]
        cleaned_price = form.cleaned_data["price"]
        cleaned_supplier = form.cleaned_data["supplier_name"]
        fare = form.cleaned_data.get("transport")
        transport = fare if fare else Decimal("0.00")
        diesel_list.append(
            Diesel(
                litres=cleaned_litre, price=cleaned_price,
                amount=cleaned_price*cleaned_litre, 
                total=(cleaned_price*cleaned_litre)+transport,
                supplier_name=cleaned_supplier.title(),
                created_by_user_id=user_id,
                month=timezone.now().strftime('%B'),
                transport=transport, created_by=user_name
            )
        )
    return diesel_list
    
def create(diesel_list:list) -> dict | None:
    try:
        with transaction.atomic():
            dieselCreate(diesel_list)
    except IntegrityError:
        return queue_error
    except Exception:
        return server_error
    return None
            

def update(
        form:DieselForm, diesel:Diesel, user, user_name
    ) -> dict | None:
    price = form.cleaned_data.get("price", diesel.price)
    litres = form.cleaned_data.get("litres", diesel.litres) 
    tfare = form.cleaned_data.get('transport', diesel.transport)
    supplier = form.cleaned_data.get(
        "supplier_name", diesel.supplier_name).title()
    try:
        with transaction.atomic():
            dieselUpdate(
                diesel, price, litres, tfare, 
                supplier, user, user_name 
            )
    except DatabaseError:
        return queue_error
    except Exception:
        return server_error
    return None

def delete_one(diesel:Diesel) -> dict | None:
    try:
        with transaction.atomic():
            Diesel.objects.select_for_update(
                nowait=True).get(
                id=diesel.id
            ).delete()
    except DatabaseError:
        return queue_error
    except Exception:
        return server_error
    return None

def delete_many(diesel_ids) -> dict | None:
    try:
        with transaction.atomic():
            Diesel.objects.select_for_update(
                nowait=True).filter(
                id__in=diesel_ids
            ).delete()
    except DatabaseError:
        return queue_error
    except Exception:
        return server_error
    return None