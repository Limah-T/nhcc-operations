from django.utils import timezone
from django.db import transaction, IntegrityError, DatabaseError
from nhcc_operations.services.generic_service import (
    server_error, queue_error
)
from decimal import Decimal
from ..models import Expense
from ..forms import ExpenseForm

def expenseRetrieval(pk) -> Expense | None:
    return Expense.objects.select_related(
        "category").filter(id=pk).first()

def expenseQueryset() -> Expense:
    return Expense.objects.select_related(
        "category").all().order_by("category__name")

def totalMonthlyExpenses(queryset:Expense) -> int:
    now = timezone.now()
    return sum(
        item.total for item in queryset if (
            item.created_at.month and item.created_at.year
        ) == (now.month and now.year)
    )


def totalAnnualExpenses(queryset:Expense) -> int:
    now = timezone.now()
    return sum(
            item.amount for item in queryset
            if (item.created_at.year == now.year)
    )

def expenseFormValidator(
        category, name, amount, quantity, date
    ) -> ExpenseForm:
    return ExpenseForm(
        data={
            "category":category,
            "name":name, 
            "amount":amount,
            "quantity":quantity,
            "date":date
        }
    )

def processCreate(
        categories, names, amounts, quantities, dates, user, full_name
    ) -> ExpenseForm | list:
    expense_list = []
    for category, name, amount, quantity, date in zip(
        categories, names, amounts, quantities, dates
    ):
        form = expenseFormValidator(
            category, name, amount, quantity, date
        )
        if not form.is_valid(): return form
        now = timezone.now()
        input_date = form.cleaned_data.get("date")
        if input_date:
            if (input_date.month == now.month) and (input_date.year == now.year):
                pass
            else:
                form.add_error("date", "Month mismatch.")
                return form        
        expense_list.append(
            Expense(
                category_id=category,
                name=name.title(), amount=amount,
                quantity=quantity,
                total=Decimal(quantity)*Decimal(amount), 
                created_by_user=user, created_by=full_name,
                created_at=input_date if input_date else timezone.now())
        )
    return expense_list

def expenseCreate(expense_list:list) -> None:
    Expense.objects.bulk_create(expense_list)

def expenseUpdate(
        expense_id, category, name, quantity, 
        amount, date, user_id, full_name
    ) -> None:
    Expense.objects.filter(
        id=expense_id).update(
            category_id=category,
            name=name.title(),
            quantity=quantity,
            amount=amount,
            total=Decimal(quantity)*Decimal(amount),
            created_at=date,
            updated_by_user_id=user_id,
            updated_by=full_name
        )
    return None

def create(expense_list:list) -> dict | None:
    try:
        with transaction.atomic():
            expenseCreate(expense_list)
    except IntegrityError:
        return queue_error
    except Exception:
        return server_error
    return None

def update(
        expense:Expense, category, name, 
        quantity, amount, date, user, full_name
    ) -> dict | None:
    try:
        with transaction.atomic():
            expenseUpdate(
                expense.id, category, name, quantity, 
                amount, date, user.id, full_name
            )
    except IntegrityError:
        return queue_error
    except Exception as e:
        return server_error
    return None

def delete_one(expense:Expense) -> dict | None:
    try:
        with transaction.atomic():
            Expense.objects.select_for_update(
                nowait=True).get(
                id=expense.id
            ).delete()
    except DatabaseError:
        return queue_error
    except Exception:
        return server_error
    return None

def delete_many(expense_ids) -> dict | None:
    try:
        with transaction.atomic():
            Expense.objects.select_for_update(
                nowait=True).filter(
                id__in=expense_ids
            ).delete()
    except DatabaseError:
        return queue_error
    except Exception:
        return server_error
    return None