from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from core.utils.helper_functions import set_date
from finance.expense.services.diesel_service import (
    DieselDataRetrieval, DieselRecordCalculator, 
)
from finance.expense.services.electricity_service import (
    EKedcDataRetrieval, EkedcRecordCalculator
)
from finance.expense.services.expense_service import (
    ExpenseDataRetrieval, total_expense_records
)
from account.services.profile_service import getNameAvatar

dashboard_temp_name = "dashboard/dashboard.html"
expense_temp_name = "dashboard/office_expense_dashboard.html"
expense_record_temp_name = "dashboard/office_expense_record.html"
category_temp_name = "dashboard/office_expense_category.html"
diesel_temp_name = "dashboard/office_expense_diesel.html"
electricity_temp_name = "dashboard/office_expense_electricity.html"
staff_account_temp_name = "dashboard/office_staff_account.html"
director_temp_name = "dashboard/director_records.html"
report_temp_name = "dashboard/office_report.html"

def get_greeting():
    hour = timezone.localtime().hour

    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Good night"

@method_decorator(login_required, name="dispatch") 
class Dashboard(View):

    def get(self, request):
        start_date, end_date = set_date()
        year = timezone.now().year

        expense_qs = ExpenseDataRetrieval()
        monthly_expenses = expense_qs.retrieve_all_with_category(start_date, end_date)
        yearly_expense_records = expense_qs.retrieve_yearly_expenses(year)

        ekedc_qs = EKedcDataRetrieval()
        monthly_ekedc = ekedc_qs.retrieve_by_month(start_date, end_date)
        yearly_ekedc_records = ekedc_qs.retrieve_by_year(year)

        diesel_qs = DieselDataRetrieval()
        monthly_diesel = diesel_qs.retrieve_by_month(start_date, end_date)
        yearly_diesel_records = diesel_qs.retrieve_by_year(year)

        ekedc_calculator = EkedcRecordCalculator()
        diesel_calculator = DieselRecordCalculator()

        total_ekedc = ekedc_calculator.total_ekedc_records(monthly_ekedc)
        total_diesel = diesel_calculator.total_records(monthly_diesel)
        total_expenses = total_expense_records(monthly_expenses)

        yearly_ekdc = ekedc_calculator.total_ekedc_records(yearly_ekedc_records)
        yearly_diesel = diesel_calculator.total_records(yearly_diesel_records)
        yearly_expenses = total_expense_records(yearly_expense_records)

        monthly_expenditure = total_ekedc+total_diesel+total_expenses
        yearly_expenditure = yearly_ekdc+yearly_diesel+yearly_expenses

        return render(
            request, dashboard_temp_name,
            context={
                "greet":get_greeting(), 
                "now":timezone.localtime(),
                "monthly_expenses":total_expenses,
                "yearly_expenses": yearly_expenses,
                "monthly_expenditure": monthly_expenditure,
                "yearly_expenditure": yearly_expenditure,
                "total_diesel":total_diesel,
                "total_ekedc":total_ekedc,
                "total_expenses": total_expenses,
                "user_name":getNameAvatar(request.user)
            }
        )
    
    def post(self, request):
        return render(request, dashboard_temp_name)




