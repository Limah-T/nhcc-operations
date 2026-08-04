from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from finance.expense.services.diesel_service import (
    DieselDataRetrieval, DieselRecordCalculator, 
)
from finance.expense.services.electricity_service import (
    EKedcDataRetrieval, EkedcRecordCalculator
)
from finance.expense.services.expense_service import (
    ExpenseDataRetrieval, ExpenseRecordCalculator
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
        expenses = ExpenseDataRetrieval().retrieve_all_with_category()
        ekedc = EKedcDataRetrieval().retrieve_by_month()
        diesel = DieselDataRetrieval().retrieve_by_month()

        expense_calculator = ExpenseRecordCalculator()
        ekedc_calculator = EkedcRecordCalculator()
        diesel_calculator = DieselRecordCalculator()

        total_ekedc = ekedc_calculator.total_monthly_amount(ekedc)
        total_diesel = diesel_calculator.monthly_total(diesel)
        total_expenses = expense_calculator.total_monthly_records(expenses)

        yearly_ekdc = ekedc_calculator.total_annual_amount(ekedc)
        yearly_diesel = diesel_calculator.total_annual_records(diesel)
        yearly_expenses = expense_calculator.total_annual_records(expenses)

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




