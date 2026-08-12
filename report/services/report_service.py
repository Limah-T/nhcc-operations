from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from pathlib import Path
from django.conf import settings
from account.services.profile_service import getFullName
from finance.expense.services.expense_service import (
    ExpenseDataRetrieval, total_expense_records, expenseOrganizer
)
from finance.expense.services.diesel_service import (
    DieselDataRetrieval, DieselRecordCalculator
)
from finance.expense.services.electricity_service import (
    EKedcDataRetrieval, EkedcRecordCalculator
)
from finance.expense.models import EKEDC, Diesel, Expense
from staff.models import StaffSalary

report_url_name = "reports"
expense_report_temp = "report/expenses.html"
expense_ekedc_report_temp = "report/expenses_and_ekedc.html"
diesel_report_temp = "report/diesel.html"
ekedc_report_temp = "report/ekedc.html"
monthly_expenditure_report_temp = "report/monthly_expenditure.html"
yearly_expenditure_report_temp = "report/yearly_expenditure.html"

def build_image_url():
    return (Path(settings.STATIC_ROOT) / "images" / "logo.png").as_uri()

def monthly_diesel_cxt_data(user, start_date, end_date, month, year)-> dict:
    queryset = DieselDataRetrieval().retrieve_by_month(start_date, end_date)
    diesel = DieselRecordCalculator()
    total_diesel = diesel.total_records(queryset)
    total_litres = diesel.total_litre_records(queryset)
    total_transport = diesel.total_transport_records(queryset)
    total_amount = diesel.total_amount_records(queryset)
    prepared_by = getFullName(user)
    generated_at = timezone.now()

    return {
        "diesel_records":queryset,
        "grand_total":total_diesel,
        "total_litres": total_litres,
        "total_transport": total_transport,
        "total_amount": total_amount,
        "total_records":queryset.count(),
        "prepared_by":prepared_by,
        "generated_at":generated_at,
        "month": month, "year": year,
        "report_period": f"{start_date:%d %b %Y} - {end_date:%d %b %Y}", 
    }

def monthly_ekedc_cxt_data(user, start_date, end_date, month, year)-> dict:
    queryset = EKedcDataRetrieval().retrieve_by_month(start_date, end_date)
    total_ekedc = EkedcRecordCalculator().total_ekedc_records(queryset)
    prepared_by = getFullName(user)
    generated_at = timezone.now()

    return {
        "ekedc_records":queryset,
        "total_ekedc":total_ekedc,
        "total_records":queryset.count(),
        "prepared_by":prepared_by,
        "generated_at":generated_at,
        "month": month, "year": year,
        "report_period": f"{start_date:%d %b %Y} - {end_date:%d %b %Y}", 
    }

def monthly_expenses_cxt_data(user, start_date, end_date, month, year)-> dict:
    queryset = ExpenseDataRetrieval().retrieve_all_with_category(start_date, end_date)
    total_expenses = total_expense_records(queryset)
    total_records = queryset.count()
    prepared_by = getFullName(user)
    generated_at = timezone.now()
    return {
        "expenses":expenseOrganizer(queryset),
        "total_expenses":total_expenses,
        "total_records":total_records,
        "prepared_by":prepared_by,
        "generated_at":generated_at,
        "month": month, "year": year,
        "report_period": f"{start_date:%d %b %Y} - {end_date:%d %b %Y}", 
    }

def monthly_expenses_ekedc_cxt_data(user, start_date, end_date, month, year)-> dict:
    queryset = ExpenseDataRetrieval().retrieve_all_with_category(start_date, end_date)
    total_expenses = total_expense_records(queryset)

    ekedc_queryset = EKedcDataRetrieval().retrieve_by_month(start_date, end_date)
    total_ekedc = EkedcRecordCalculator().total_ekedc_records(ekedc_queryset)
    total_records = queryset.count()
    grand_total = total_ekedc + total_expenses
    prepared_by = getFullName(user)
    generated_at = timezone.now()

    return {
        "expense_records":expenseOrganizer(queryset),
        "total_records":total_records + ekedc_queryset.count(),
        "total_ekedc": total_ekedc,
        "ekedc_records": ekedc_queryset,
        "prepared_by":prepared_by,
        "grand_total": grand_total,
        "generated_at":generated_at,
        "month": month, "year": year,
        "report_period": f"{start_date:%d %b %Y} - {end_date:%d %b %Y}", 
    }

def monthly_expenditure_cxt_data(user, start_date, end_date, month, year):
    expense_queryset = ExpenseDataRetrieval().retrieve_all_with_category(
        start_date, end_date)
    diesel_queryset = DieselDataRetrieval().retrieve_by_month(start_date, end_date)
    ekedc_queryset = EKedcDataRetrieval().retrieve_by_month(start_date, end_date)

    total_expenses = total_expense_records(expense_queryset)
    diesel = DieselRecordCalculator()
    total_diesel = diesel.total_records(diesel_queryset)
    total_litres = diesel.total_litre_records(diesel_queryset)
    total_transport = diesel.total_transport_records(diesel_queryset)
    ekedc = EkedcRecordCalculator()
    total_ekedc = ekedc.total_ekedc_records(ekedc_queryset)
    total_kwhs = ekedc.total_kwh_records(ekedc_queryset)

    expense_records = expense_queryset.count()
    diesel_records = diesel_queryset.count()
    ekedc_records = ekedc_queryset.count()

    grand_total = total_expenses+total_diesel+total_ekedc
    salaries = {}
    salary_records = 0
    total_salaries = 0
    prepared_by = getFullName(user)
    generated_at = timezone.now()
    return {
        "month": month, "year": year,

        # Summary
        "expense_records": expense_records,
        "diesel_records": diesel_records,
        "ekedc_records": ekedc_records,
        "salary_records": salary_records,

        # Office Expenses
        "total_expenses": total_expenses,

        # Diesel
        "total_diesel": total_diesel, "total_litres": total_litres,
        "total_transport": total_transport,

        # EKEDC
        "total_ekedc": total_ekedc, "total_kwhs": total_kwhs,

        # Staff Salaries
        "salaries": salaries, "total_salaries": total_salaries,

        # Overall
        "grand_total": grand_total,

        # Report information
        "prepared_by": prepared_by, "generated_at": generated_at,
        "report_period": f"{start_date:%d %b %Y} - {end_date:%d %b %Y}", 
    }

def expense_yearly_expenditure(year) -> dict:
    expense_queryset = (
    Expense.objects
        .filter(created_at__year=year)
        .annotate(report_month=TruncMonth("created_at"))
        .values("report_month")
        .annotate(total=Sum("total"))
    )

    return {
        row["report_month"].strftime("%B"): row["total"]
        for row in expense_queryset
    }

def diesel_yearly_expenditure(year):
    diesel_queryset = (
        Diesel.objects
        .filter(created_at__year=year)
        .annotate(report_month=TruncMonth("created_at"))
        .values("report_month")
        .annotate(total=Sum("total"))
    )

    return {
        row["report_month"].strftime("%B"): row["total"]
        for row in diesel_queryset
    }

def ekedc_yearly_expenditure(year):
    ekedc_queryset = (
        EKEDC.objects
        .filter(created_at__year=year)
        .annotate(report_month=TruncMonth("created_at"))
        .values("report_month")
        .annotate(total=Sum("amount"))
    )

    return {
        row["report_month"].strftime("%B"): row["total"]
        for row in ekedc_queryset
    }

def salary_yearly_expenditure(year):
    salary_queryset = (
        StaffSalary.objects
        .filter(date_received__year=year)
        .annotate(report_month=TruncMonth("date_received"))
        .values("report_month")
        .annotate(total=Sum("amount_paid"))
    )

    salary_months = {
        row["report_month"].strftime("%B"): row["total"]
        for row in salary_queryset
    }
    return salary_months

def salary_yearly_expenditure(year):
    salary_queryset = (
        StaffSalary.objects
        .select_related("staff")
        .filter(date_received__year=year)
        .annotate(
            report_month=TruncMonth("date_received")
        )
        .values(
            "staff_id",
            "staff__first_name",
            "staff__last_name",
            "report_month",
        )
        .annotate(
            total=Sum("amount_paid")
        )
        .order_by(
            "staff__first_name",
            "staff__last_name",
            "report_month",
        )
    )

    salary_data = {}

    for row in salary_queryset:
        staff_id = row["staff_id"]

        if staff_id not in salary_data:
            salary_data[staff_id] = {
                "name": (
                    f'{row["staff__first_name"]} '
                    f'{row["staff__last_name"]}'
                ),
                "total": 0,
            }

            for month in MONTHS:
                salary_data[staff_id][month[:3].lower()] = 0

        month_key = row["report_month"].strftime("%B")[:3].lower()

        salary_data[staff_id][month_key] = row["total"]
        salary_data[staff_id]["total"] += row["total"]

    return list(salary_data.values())



MONTHS = (
    "January", "February", "March",
    "April", "May", "June",
    "July", "August", "September",
    "October", "November", "December",
)


def yearly_expenditure_cxt_data(user, year=None)-> dict:
    if year is None: year = timezone.now().year
    diesel = diesel_yearly_expenditure(year)
    expense = expense_yearly_expenditure(year)
    ekedc = ekedc_yearly_expenditure(year)
    salary = salary_yearly_expenditure(year)
    yearly_data = [
            {
                "name": "Office Expenses",
                "total": sum(expense.values()),
                **{
                    month[:3].lower(): expense.get(month, 0)
                    for month in MONTHS
                },
            },
            {
                "name": "Diesel",
                "total": sum(diesel.values()),
                **{
                    month[:3].lower(): diesel.get(month, 0)
                    for month in MONTHS
                },
                
            },
            {
                "name": "Electricity (Prepaid Meter)",
                "total": sum(ekedc.values()),
                **{
                    month[:3].lower(): ekedc.get(month, 0)
                    for month in MONTHS
                },
            },
            {
                "name": "Staff Salaries",
                **{
                    month[:3].lower(): salary.get(month, 0)
                    for month in MONTHS
                },
            },
        ]
    january_total = sum(item["jan"] for item in yearly_data)
    february_total = sum(item["feb"] for item in yearly_data)
    march_total = sum(item["mar"] for item in yearly_data)
    april_total = sum(item["apr"] for item in yearly_data)
    may_total = sum(item["may"] for item in yearly_data)
    june_total = sum(item["jun"] for item in yearly_data)
    july_total = sum(item["jul"] for item in yearly_data)
    august_total = sum(item["aug"] for item in yearly_data)
    september_total = sum(item["sep"] for item in yearly_data)
    october_total = sum(item["oct"] for item in yearly_data)
    november_total = sum(item["nov"] for item in yearly_data)
    december_total = sum(item["dec"] for item in yearly_data)

    yearly_grand_total = (
        january_total +
        february_total +
        march_total +
        april_total +
        may_total +
        june_total +
        july_total +
        august_total +
        september_total +
        october_total +
        november_total +
        december_total
    )
    prepared_by = getFullName(user)
    generated_at = timezone.now()
    return {

        "generated_at":generated_at,
        "prepared_by":prepared_by,
        "year": year,
        "yearly_data": yearly_data,
        "january_total": january_total,
        "february_total": february_total,
        "march_total": march_total,
        "april_total": april_total,
        "may_total": may_total,
        "june_total": june_total,
        "july_total": july_total,
        "august_total": august_total,
        "september_total": september_total,
        "october_total": october_total,
        "november_total": november_total,
        "december_total": december_total,
        "yearly_grand_total": yearly_grand_total,
        "report_period": f"1 January {year} – 31 December {year}", 
    }


def get_template_context(
        report_type, user, start, end, month, year
    )-> dict:
    if report_type == "expense":
        return {
            "template":expense_report_temp, 
            "context":monthly_expenses_cxt_data(
                user, start, end, month, year
            )
        }
    if report_type == "expense_ekedc":
        return {
            "template":expense_ekedc_report_temp, 
            "context":monthly_expenses_ekedc_cxt_data(
                user, start, end, month, year
            )
        }
    if report_type == "diesel":
        return {
            "template":diesel_report_temp, 
            "context":monthly_diesel_cxt_data(
                user, start, end, month, year
            )
        }
    if report_type == "electricity":
        return {
            "template":ekedc_report_temp, 
            "context":monthly_ekedc_cxt_data(
                user, start, end, month, year
            )
        }
    if report_type == "monthly":
        return {
            "template":monthly_expenditure_report_temp,
            "context":monthly_expenditure_cxt_data(
                user, start, end, month, year
            )
        }
    return {
        "template":yearly_expenditure_report_temp,
        "context":yearly_expenditure_cxt_data(user, year)
    }

