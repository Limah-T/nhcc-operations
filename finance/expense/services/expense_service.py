from django.db import transaction, IntegrityError, DatabaseError
from django.utils import timezone
from django.http.request import HttpRequest
from nhcc_operations.services.generic_service import (
    server_error, queue_error, expense_404, no_changes, date_constructor
)
from decimal import Decimal
from account.services.profile_service import getFullName, getNameAvatar
from ..services.category_service import CategoryDataRetrieval
from ..models import Expense

class ExpensePayloadParser:
    def __init__(self, request:HttpRequest):
        self.request = request

    def parse_single(self) -> dict:
        return {
            "category": self.request.POST.get("category"),
            "name": self.request.POST.get("name"),
            "amount": self.request.POST.get("amount"),
            "quantity": self.request.POST.get("quantity"),
            "date": self.request.POST.get("date")
        }

    def parse_bulk(self) -> dict:
        return {
            "category": self.request.POST.getlist("category"),
            "name": self.request.POST.getlist("name"),
            "amount": self.request.POST.getlist("amount"),
            "quantity": self.request.POST.getlist("quantity"),
            "date": self.request.POST.getlist("date")
        }

class ExpenseRecordCalculator:
    def __init__(self):
        self.current_month = timezone.now().month
        self.current_year = timezone.now().year

    def total_monthly_records(
            self, queryset:Expense, start_date=None, end_date=None
        ) -> Decimal:
        if start_date and end_date:
            return sum(
                item.total for item in queryset 
                if item.created_at and (
                    item.created_at.month == start_date.month and 
                    item.created_at.year == end_date.year
                ) 
            )

        return sum(
            item.total for item in queryset 
            if item.created_at and (
                item.created_at.month == self.current_month and 
                item.created_at.year == self.current_year
            ) 
        )

    def count_monthly_records(
            self, start_date=None, end_date=None) -> int:
        if start_date and end_date:
            return Expense.objects.filter(
                    created_at__gte=start_date, 
                    created_at__lte=end_date
            ).count()
        
        now = timezone.now()
        start_date, end_date = date_constructor(now.year, now.month)
        return Expense.objects.filter(
                created_at__gte=start_date, 
                created_at__lte=end_date
        ).count()

    def total_annual_records(
            self, queryset:Expense, year:int=None) -> Decimal:
        if year:
            return sum(
                item.total for item in queryset
                if item.created_at and (item.created_at.year == year)
            )
        return sum(
                item.total for item in queryset
                if item.created_at and (
                    item.created_at.year == self.current_year
                )
        )
    

class ExpenseDataRetrieval:

    @staticmethod
    def retrieve_one(pk) -> Expense | None:
        return Expense.objects.select_related(
            "category").filter(id=pk).first()

    @staticmethod
    def retrieve_all_with_category(start_date=None, end_date=None) -> Expense:
        if start_date and end_date:
            return Expense.objects.select_related(
                "category").filter(
                    created_at__gte=start_date, 
                    created_at__lt=end_date
                ).order_by("category__name")
        
        now = timezone.now()
        start_date, end_date = date_constructor(now.year, now.month)
        return Expense.objects.select_related(
            "category").filter(
                created_at__gte=start_date, 
                created_at__lt=end_date
            ).order_by("category__name")

    @staticmethod
    def retrieve_locked_bulk_expenses(expense_ids) -> Expense:
        return Expense.objects.select_for_update(
            nowait=True).filter(
            id__in=expense_ids
        )

def expense_context_data(user):
    categories = CategoryDataRetrieval().retrieve_all()
    expenses = ExpenseDataRetrieval().retrieve_all_with_category()
    calculator = ExpenseRecordCalculator()
    total_expenses = calculator.total_monthly_records(expenses)
    
    return {
        "categories":categories,
        "expenses":expenses,
        "count":expenses.count(),
        "monthly_total_display": f"₦{total_expenses:,.2f}",
        "user_name":getNameAvatar(user),
    }

def expenseOrganizer(queryset:Expense) -> dict:
    expenses = {}
    for query in queryset:
        category = query.category_name
        data = expenses.get(category)
        if data:
            data["expenses"].append({
                    "name": query.name,
                    "amount": query.amount,
                    "quantity": query.quantity,
                    "total": query.total,
                    "created_at": query.created_at
                })
            data["rowspan"] = len(data["expenses"])
        else:
            data = [
                {
                    "name": query.name,
                    "amount": query.amount,
                    "quantity": query.quantity,
                    "total": query.total,
                    "created_at": query.created_at
                }
            ]
            expenses.update({
                category: {
                    "rowspan": len(data),
                    "expenses": data
                }
            })

    return expenses


class ExpenseDataInserter:
    def __init__(self, data:list[dict] | dict, user):
        
        self.data = data
        self.user = user
        self.full_name = getFullName(user)

    def insert_one(self):
        Expense.objects.create(
            category=self.data["category"],
            category_name=self.data["category"].name,
            name=self.data["name"], 
            amount=self.data["amount"],
            quantity=self.data["quantity"],
            total=Decimal(self.data["quantity"])*Decimal(self.data["amount"]), 
            created_by_user=self.user, 
            created_by=self.full_name,
            created_at=self.data["date"]
    )

    def insert_many(self) -> None:
        expenses = []
        for expense in self.data:
            expenses.append(
                Expense(
                    category=expense["category"],
                    category_name=expense["category"].name,
                    name=expense["name"], 
                    amount=expense["amount"],
                    quantity=expense["quantity"],
                    total=Decimal(expense["quantity"])*Decimal(expense["amount"]), 
                    created_by_user=self.user, 
                    created_by=self.full_name,
                    created_at=expense["date"]
            ))
        Expense.objects.bulk_create(expenses)

class ExpenseDataUpdater:

    @staticmethod
    def can_update(expense:Expense, data:dict) -> bool:
        for key,value in data.items():
            if key == "date":
                if expense.created_at != value:
                    return True
            else:
                if getattr(expense, key) != value:
                    return True
        return False

    @staticmethod
    def update_one(expense_id, data:dict, user) -> None:
        qty = data["quantity"]
        amt = data["amount"]
        Expense.objects.filter(
            id=expense_id).update(
                category=data["category"],
                category_name=data["category"].name,
                name=data["name"], quantity=qty,
                amount=amt, total=qty*amt,
                created_at=data["date"],
                updated_by_user=user,
                updated_by=getFullName(user)
            )

class ExpenseDeleteData:

    @staticmethod
    def delete_one(id) -> None:
        Expense.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    @staticmethod
    def delete_many(expenses:Expense) -> None:
        expenses.delete()



"""################# HELPER FUNCTIONS##############"""

def create_single(data:dict, user) -> tuple[str, int] | None:
    try:
        ExpenseDataInserter(data, user).insert_one()
    except Exception:
        return (server_error, 500)
    return None

def create_bulk(data:list[dict], user) -> tuple[str, int] | None:
    try:
        ExpenseDataInserter(data, user).insert_many()
    except Exception:
        return (server_error, 500)
    return None

def update_single(id, data:dict, user) -> tuple[str, int] | None:
    try:
        expense = ExpenseDataRetrieval().retrieve_one(id)
        if expense is None:
            return (expense_404, 404)
        updater = ExpenseDataUpdater()
        if not updater.can_update(expense, data):
            return (no_changes, 400)
        with transaction.atomic():
            updater.update_one(expense.id, data, user)
    except IntegrityError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None


def delete_single(expense_id) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            ExpenseDeleteData().delete_one(expense_id)
    except Expense.DoesNotExist:
        return (expense_404, 404)
    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None

def delete_bulk(expense_ids) -> tuple[str, int] | None:
    try:
        with transaction.atomic():
            expenses = ExpenseDataRetrieval(
                ).retrieve_locked_bulk_expenses(expense_ids)
            if not expenses.exists():
                return (expense_404, 404)
            ExpenseDeleteData().delete_many(expenses)
    except DatabaseError:
        return (queue_error, 400)
    except Exception:
        return (server_error, 500)
    return None