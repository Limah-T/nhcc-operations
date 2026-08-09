from django.db import transaction, DatabaseError
from django.utils import timezone
from django.http.request import HttpRequest
from decimal import Decimal
from account.services.profile_service import getFullName, getNameAvatar
from core.utils.custom_exceptions import NothingToUpdateError
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

def total_expense_records(queryset:Expense) -> Decimal:
    return sum(
        item.total for item in queryset
    )           

class ExpenseDataRetrieval:

    @staticmethod
    def retrieve_one(pk) -> Expense | None:
        return Expense.objects.select_related(
            "category").filter(id=pk).first()

    @staticmethod
    def retrieve_all_with_category(start_date, end_date) -> Expense:
        return Expense.objects.select_related(
            "category").filter(
                created_at__gte=start_date, 
                created_at__lte=end_date
            ).order_by("category__name", "created_at")

    @staticmethod
    def retrieve_yearly_expenses(year:int) -> Expense:
        return Expense.objects.filter(created_at__year=year)

    @staticmethod
    def retrieve_locked_bulk_expenses(expense_ids) -> Expense:
        return Expense.objects.select_for_update(
            nowait=True).filter(
            id__in=expense_ids
        )

def expense_context_data(user, start_date, end_date, form=None):
    categories = CategoryDataRetrieval().retrieve_all()
    expenses = ExpenseDataRetrieval().retrieve_all_with_category(
        start_date, end_date)
    total_expenses = total_expense_records(expenses)
    
    return {
        "categories":categories,
        "expenses":expenses,
        "count":expenses.count(),
        "monthly_total_display": f"₦{total_expenses:,.2f}",
        "user_name":getNameAvatar(user),
        "form": form
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
                    "created_at": query.created_at,
                    "date_recorded": query.date_recorded
                })
            data["rowspan"] = len(data["expenses"])
        else:
            data = [
                {
                    "name": query.name,
                    "amount": query.amount,
                    "quantity": query.quantity,
                    "total": query.total,
                    "created_at": query.created_at,
                    "date_recorded":query.date_recorded
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
        Expense.objects.create(
            category=self.data["category"],
            category_name=self.data["category"].name,
            name=self.data["name"], 
            amount=self.data["amount"],
            quantity=self.data["quantity"],
            total=Decimal(self.data["quantity"])*Decimal(self.data["amount"]), 
            created_by_user=self.user, 
            created_by=self.full_name,
            created_at=self.data["date"],
            date_recorded=timezone.now().date()
    )

    def _insert_many(self) -> None:
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
                    created_at=expense["date"],
                    date_recorded=timezone.now().date()
            ))
        Expense.objects.bulk_create(expenses)

class ExpenseDataUpdater:

    def __init__(self, data:dict, user):
        self.data = data
        self.user = user

    def update_single(self, id) -> None:
        try:
            expense = ExpenseDataRetrieval().retrieve_one(id)
            if expense is None:
                raise Expense.DoesNotExist
            if not self._can_update(expense):
                raise NothingToUpdateError
            with transaction.atomic():
                self._update_one(expense.id)
        except DatabaseError:
            raise 
        except Exception:
            raise

    def _can_update(self, expense:Expense) -> bool:
        for key,value in self.data.items():
            if key == "date":
                if expense.created_at != value:
                    return True
            else:
                if getattr(expense, key) != value:
                    return True
        return False

    def _update_one(self, expense_id) -> None:
        qty, amt  = self.data["quantity"], self.data["amount"]
        Expense.objects.filter(
            id=expense_id).update(
                category=self.data["category"],
                category_name=self.data["category"].name,
                name=self.data["name"], quantity=qty,
                amount=amt, total=qty*amt,
                created_at=self.data["date"],
                updated_by_user=self.user,
                updated_by=getFullName(self.user)
            )

class ExpenseDataDeleter:

    def delete_single(self, expense_id) -> None:
        try:
            with transaction.atomic():
                self._delete_one(expense_id)
        except Expense.DoesNotExist:
            raise
        except DatabaseError:
            raise
        except Exception:
            raise

    def delete_bulk(self, expense_ids) -> None:
        try:
            with transaction.atomic():
                expenses = self._lock_expense_list(expense_ids)
                if not expenses.exists():
                    raise Expense.DoesNotExist
                expenses.delete()
        except DatabaseError:
            raise
        except Exception:
            raise

    def _delete_one(self, id) -> None:
        Expense.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    def _lock_expense_list(self, expense_ids:list) -> Expense:
        return Expense.objects.select_for_update(
        nowait=True).filter(
            id__in=expense_ids
        )
