from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from weasyprint import HTML
from account.services.profile_service import getFullName
# from finance.expense.services.expense_service import (
#     expenseQueryset, totalMonthlyExpenses, 
#     totalExpenseRecords, expenseOrganizer
# )
# from finance.expense.services.diesel_service import (
#     dieselQueryset, totalMonthlyDiesel, totaldieselRecords
# )
# from finance.expense.services.electricity_service import (
#     ekedcQuerySet, totalMonthlyPrepaid, totalEkedcRecords
# )
import calendar

url_name = "reports"
expense_report_temp = "report/expenses.html"
monthly_expenditure_report_temp = "report/monthly_expenditure.html"


def monthly_expenses_cxt_data(request, start_date, end_date, month, year)-> dict:
    queryset = expenseQueryset()
    total_expenses = totalMonthlyExpenses(queryset)
    total_records = totalExpenseRecords(start_date, end_date)
    prepared_by = getFullName(request)
    generated_at = timezone.now()
    return {
        "expenses":expenseOrganizer(queryset),
        "total_expenses":total_expenses,
        "total_records":total_records,
        "prepared_by":prepared_by,
        "generated_at":generated_at,
        "month": month,
        "year": year,
        "report_period": f"{start_date:%d %b %Y} - {end_date:%d %b %Y}",   
    }

def monthly_expenditure_cxt_data(request, start_date, end_date, month, year):
    expense_queryset = expenseQueryset()
    diesel_queryset = dieselQueryset()
    ekedc_queryset = ekedcQuerySet()

    total_expenses = totalMonthlyExpenses(expenseQueryset())
    total_diesel = totalMonthlyDiesel(dieselQueryset())
    total_ekedc = totalMonthlyPrepaid(ekedcQuerySet())

    expense_records = totalExpenseRecords(start_date, end_date)
    diesel_records = totaldieselRecords(start_date, end_date)
    ekedc_records = totalEkedcRecords(start_date, end_date)

    expenses =  expenseOrganizer(expense_queryset)
    grand_total = total_expenses+total_diesel+total_ekedc

    prepared_by = getFullName(request)
    generated_at = timezone.now()
    return {
        "month": month, "year": year,

        # Summary
        "expense_records": expense_records,
        "diesel_records": diesel_records,
        "ekedc_records": ekedc_records,
        "salary_records": {},

        # Office Expenses
        "expenses":expenses, "total_expenses": total_expenses,

        # Diesel
        "diesel": diesel_queryset, "diesel_total": total_diesel,

        # EKEDC
        "ekedc": ekedc_queryset, "ekedc_total": total_ekedc,

        # Staff Salaries
        "salaries": {}, "salary_total": {},

        # Overall
        "grand_total": grand_total,

        # Report information
        "generated_by": prepared_by, "generated_at": generated_at,
    }

def getTemplateContext(
        report_type, request, start, end, month, year
    )-> dict:
    if report_type == "expense":
        return {
            "template":expense_report_temp, 
            "context":monthly_expenses_cxt_data(
                request, start, end, month, year
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
                request, start, end, month, year
            )
        }
    return ...

def fileNamingConstructor(type, month, year, start, end) -> str:
    return f"{month}_{year}_{start.day}_to_{end.day}_{type.lower()}.pdf"

def setDate() -> tuple:
    now = timezone.now()
    month, year = now.month, now.year
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, getMonthDays()).date()
    return (start_date, end_date)

def futureDate(start_date, end_date) -> bool:
    now = timezone.now()
    if (
            start_date.month > now.month or start_date.year > now.year
            ) or( end_date.month > now.month or end_date.year > now.year):
            
        return True
    return False

def setMonthYear() -> tuple:
    now = timezone.now()
    return (now.strftime("%B"), now.strftime("%Y"))

def getMonthDays() -> int:
    now = timezone.now()
    _, num_of_days = calendar.monthrange(now.year, now.month)
    return num_of_days

def pdfGenerator(
        html_string, request, file_name
    ) -> HttpResponse:
    pdf =  HTML(
        string=html_string,
        base_url=request.build_absolute_uri("/")
    ).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'
    return response

