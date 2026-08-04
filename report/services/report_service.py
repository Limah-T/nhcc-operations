from django.utils import timezone
from pathlib import Path
from django.conf import settings
from account.services.profile_service import getFullName
from finance.expense.services.expense_service import (
    ExpenseDataRetrieval, ExpenseRecordCalculator, expenseOrganizer
)
from finance.expense.services.diesel_service import (
    DieselDataRetrieval, DieselRecordCalculator
)
from finance.expense.services.electricity_service import (
    EKedcDataRetrieval, EkedcRecordCalculator
)

url_name = "reports"
expense_report_temp = "report/expenses.html"
expense_ekedc_report_temp = "report/expenses_and_ekedc.html"
diesel_report_temp = "report/diesel.html"
ekedc_report_temp = "report/ekedc.html"
monthly_expenditure_report_temp = "report/monthly_expenditure.html"

def build_image_url():
    return (Path(settings.STATIC_ROOT) / "images" / "logo.png").as_uri()

def monthly_diesel_cxt_data(user, start_date, end_date, month, year)-> dict:
    queryset = DieselDataRetrieval().retrieve_by_month(start_date, end_date)
    diesel = DieselRecordCalculator()
    total_diesel = diesel.monthly_total(queryset)
    total_litres = diesel.total_monthly_litres(queryset)
    total_transport = diesel.total_monthly_transport(queryset)
    total_amount = diesel.total_monthly_amount(queryset)
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
    ekedc = EkedcRecordCalculator()
    total_ekedc = ekedc.total_monthly_amount(queryset)
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
    expenses = ExpenseRecordCalculator()
    total_expenses = expenses.total_monthly_records(queryset)
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
    total_expenses = ExpenseRecordCalculator().total_monthly_records(queryset)

    ekedc_queryset = EKedcDataRetrieval().retrieve_by_month(start_date, end_date)
    ekedc = EkedcRecordCalculator()
    total_ekedc = ekedc.total_monthly_amount(ekedc_queryset)
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

    total_expenses = ExpenseRecordCalculator().total_monthly_records(
        expense_queryset)
    diesel = DieselRecordCalculator()
    total_diesel = diesel.monthly_total(diesel_queryset)
    total_litres = diesel.total_monthly_litres(diesel_queryset)
    total_transport = diesel.total_monthly_transport(diesel_queryset)
    ekedc = EkedcRecordCalculator()
    total_ekedc = ekedc.total_monthly_amount(ekedc_queryset)
    total_kwhs = ekedc.total_monthly_kwh(ekedc_queryset)

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
    return ...

