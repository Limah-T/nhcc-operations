from django.http import HttpResponse
from django.utils import timezone
from django.templatetags.static import static
from django.conf import settings
from pathlib import Path
from weasyprint import HTML, CSS
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
monthly_expenditure_report_temp = "report/monthly_expenditure.html"

def build_image_url():
    return (Path(settings.STATIC_ROOT) / "images" / "logo.png").as_uri()

def monthly_expenses_cxt_data(user, start_date, end_date, month, year)-> dict:
    queryset = ExpenseDataRetrieval().retrieve_all_with_category(start_date, end_date)
    expenses = ExpenseRecordCalculator()
    total_expenses = expenses.total_monthly_records(queryset, start_date, end_date)
    total_records = expenses.count_monthly_records(start_date, end_date)
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

def monthly_expenditure_cxt_data(user, start_date, end_date, month, year):
    expense_queryset = ExpenseDataRetrieval().retrieve_all_with_category(
        start_date, end_date)
    diesel_queryset = DieselDataRetrieval().retrieve_by_month(start_date, end_date)
    ekedc_queryset = EKedcDataRetrieval().retrieve_by_month(start_date, end_date)

    total_expenses = ExpenseRecordCalculator().total_monthly_records(
        expense_queryset, start_date, end_date)
    total_diesel = DieselRecordCalculator().total_monthly_records(
        diesel_queryset, start_date, end_date)
    total_ekedc = EkedcRecordCalculator().total_monthly_records(
        ekedc_queryset, start_date, end_date)

    expense_records = expense_queryset.count()
    diesel_records = diesel_queryset.count()
    ekedc_records = ekedc_queryset.count()

    expenses =  expenseOrganizer(expense_queryset)
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
        "expenses":expenses, "total_expenses": total_expenses,

        # Diesel
        "diesel": diesel_queryset, "diesel_total": total_diesel,

        # EKEDC
        "ekedc": ekedc_queryset, "ekedc_total": total_ekedc,

        # Staff Salaries
        "salaries": salaries, "salary_total": total_salaries,

        # Overall
        "grand_total": grand_total,

        # Report information
        "generated_by": prepared_by, "generated_at": generated_at,
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
    if report_type == "diesel":
        return ...
    if report_type == "electricity":
        return ...
    if report_type == "monthly":
        return {
            "template":monthly_expenditure_report_temp,
            "context":monthly_expenditure_cxt_data(
                user, start, end, month, year
            )
        }
    return ...

def file_naming_constructor(type, month, year, start, end) -> str:
    return f"{month}_{year}_{start.day}_to_{end.day}_{type.lower()}.pdf"


def pdf_generator(html_string, request, file_name):
    pdf = HTML(
        string=html_string,
        base_url=request.build_absolute_uri("/")
    ).write_pdf(
        # stylesheets=[
        #     CSS(settings.STATIC_ROOT / css_path)
        # ]
    )

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{file_name}"'
    return response
