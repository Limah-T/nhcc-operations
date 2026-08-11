from django.db import transaction, IntegrityError, DatabaseError
from django.http.request import HttpRequest
from django.utils import timezone
from core.utils.custom_exceptions import NothingToUpdateError
from account.services.profile_service import getFullName, getNameAvatar
from decimal import Decimal
from ..models import Staff, StaffSalary

salary_url_name = "salary"

class SalaryPayloadParser:
    def __init__(self, request:HttpRequest):
        self.request = request

    def parse_single(self) -> dict:
        return {
            "staff": self.request.POST.get("staff"),
            "amount_paid":self.request.POST.get("amount_paid"),
            "amount_deducted":self.request.POST.get("amount_deducted"),
            "bonus":self.request.POST.get("bonus"),
            "additional_info":self.request.POST.get("additional_info"),
            "date_received":self.request.POST.get("date_received"),
        }

    def parse_bulk(self) -> dict:
        return {
            "staff": self.request.POST.getlist("staff"),
            "amount_paid":self.request.POST.getlist("amount_paid"),
            "amount_deducted":self.request.POST.getlist("amount_deducted"),
            "bonus":self.request.POST.getlist("bonus"),
            "additional_info":self.request.POST.getlist("additional_info"),
            "date_received":self.request.POST.getlist("date_received"),
        }

class SalaryDataRetrieval:

    @staticmethod
    def retrieve_one(id) -> StaffSalary | None:
        return StaffSalary.objects.filter(id=id).first()

    @staticmethod
    def retrieve_all() -> StaffSalary:
        return StaffSalary.objects.select_related(
            "staff").all().order_by('-amount_paid', '-date_received')

    @staticmethod
    def retrieve_bulk(ids) -> StaffSalary:
        return StaffSalary.objects.select_related(
            "staff").filter(id__in=ids)

    @staticmethod
    def retrieve_by_month(start_date, end_date) -> StaffSalary:
        return StaffSalary.objects.select_related(
            "staff").filter(
            date_received__gte=start_date,
            date_received__lt=end_date
        ).order_by('created_at')

    @staticmethod
    def retrieve_by_year(year:int) -> StaffSalary:
        return StaffSalary.objects.select_related(
            "staff").filter(created_at__year=year)

def total_salary_records(queryset:StaffSalary):
    return sum(salary.amount_paid for salary in queryset)    

def salary_context_data(user, start_date, end_date) -> dict:
    queryset = SalaryDataRetrieval().retrieve_by_month(start_date, end_date)
    total = total_salary_records(queryset)

    return {
        "salary_records": queryset,
        "count": queryset.count(),
        "monthly_total_display": f"₦{total:,.2f}",
        "total_salaries":queryset.count(),
        "user_name":getNameAvatar(user)
    }

class SalaryDataInserter:
    def __init__(self, data:list[dict] | dict, user):
        
        self.data = data
        self.user = user
        self.today = timezone.now()
        self.full_name = getFullName(user)

    def create_single(self) -> None:
        try:
            with transaction.atomic():
                self._insert_one()
        except Exception:
            raise

    def create_bulk(self) ->  None:
        try:
            with transaction.atomic():
                self._insert_many()
        except Exception:
            raise

    def _insert_one(self) -> None:
        staff_full_name = self.data["staff"].first_name + self.data["staff"].last_name
        info = self.data.get("additional_info")
        main_salary = self.data["staff"].salary
        bonus, amount_deducted = Decimal("0"), Decimal("0")
        amount_paid = self.data.get("amount_paid", main_salary)
        if amount_paid > main_salary:
            bonus = amount_paid - main_salary
        else: 
            amount_deducted = main_salary - amount_paid 
        StaffSalary.objects.create(
            staff=self.data["staff"], amount_paid=amount_paid,
            amount_deducted=amount_deducted, bonus=bonus,
            additional_info= info.title() if info else None,
            date_received=self.data.get("date_received", self.today.date()),
            staff_full_name=staff_full_name,
            created_at = self.today.date(),
            created_by_user=self.user,
            created_by=self.full_name
        )
        
    def _insert_many(self) -> None:
        salary_list = []
        for salary in self.data:
            staff_full_name = salary["staff"].first_name + salary["staff"].last_name
            info = salary.get("additional_info")
            main_salary = salary["staff"].salary
            bonus, amount_deducted = Decimal("0"), Decimal("0")
            amount_paid = salary.get("amount_paid", main_salary)
            if amount_paid > main_salary:
                bonus =  amount_paid - main_salary
            else:
                amount_deducted = main_salary - amount_paid
           
            salary_list.append(
                StaffSalary(
                    staff=salary["staff"], amount_paid=amount_paid,
                    amount_deducted=amount_deducted, bonus=bonus,
                    additional_info=info.title() if info else None,
                    date_received=salary.get("date_received", self.today.date()),
                    created_at = self.today.date(),
                    staff_full_name=staff_full_name,
                    created_by_user=self.user,
                    created_by=self.full_name
            ))
        StaffSalary.objects.bulk_create(salary_list)

class SalaryDataUpdater:
    def __init__(self, data:dict, user):
        self.data = data
        self.user = user

    def update_single(self, id) -> None:
        try:
            salary = SalaryDataRetrieval().retrieve_one(id)
            if salary is None:
                raise StaffSalary.DoesNotExist
            if not self._can_update(salary):
                raise NothingToUpdateError
            with transaction.atomic():
                self._update_one(salary)
        except IntegrityError:
            raise
        except Exception:
            raise

    def _can_update(self, salary:StaffSalary) -> bool:
        for key,value in self.data.items():
            if key == "staff": continue
            if getattr(salary, key) != value:
                return True
        return False

    def _update_one(self, salary:StaffSalary) -> None:
        main_salary = salary.staff.salary
        info = self.data.get("additional_info")
        bonus, amount_deducted = salary.bonus, salary.amount_deducted
        amount_paid = self.data.get("amount_paid", salary.amount_paid)
        if amount_paid > main_salary:
            bonus =  amount_paid - main_salary
        else:
            amount_deducted = main_salary - amount_paid
        StaffSalary.objects.filter(
            id=salary.id
            ).update(
                staff=self.data.get("staff", salary.staff),
                amount_paid=amount_paid,
                amount_deducted=amount_deducted, bonus=bonus,
                additional_info=info.title() if info else None,
                date_received=self.data.get("date_received", salary.date_received),
                updated_at=timezone.now().date(),
                updated_by_user=self.user,
                updated_by=getFullName(self.user)
            )

class SalaryDataDeleter:

    def delete_single(self, salary_id) -> None:
        try:
            with transaction.atomic():
                self._delete_one(salary_id)
        except StaffSalary.DoesNotExist:
            raise
        except DatabaseError:
            raise
        except Exception:
            raise

    def delete_bulk(self, salary_ids) ->  None:
        try:
            with transaction.atomic():
                salaries = self._lock_salary_list(salary_ids)
                if not salaries.exists():
                    raise StaffSalary.DoesNotExist
                salaries.delete()
        except DatabaseError:
            raise
        except Exception:
            raise

    def _delete_one(self, id) -> None:
        StaffSalary.objects.select_for_update(
            nowait=True).get(
            id=id
        ).delete()

    def _lock_salary_list(self, salary_ids) -> StaffSalary:
        return StaffSalary.objects.select_for_update(
            nowait=True).filter(
            id__in=salary_ids
        )

