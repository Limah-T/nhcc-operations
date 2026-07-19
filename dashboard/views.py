from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from finance.expense.services.diesel_service import (
    totalMonthlyDiesel, totalAnnualDiesel, dieselQueryset, 
)
from finance.expense.services.electricity_service import (
    totalMonthlyPrepaid, totalAnnualPrepaid, ekedcQuerySet
)
from finance.expense.services.expense_service import (
    totalMonthlyExpenses, totalAnnualExpenses, expenseQueryset
)
from account.services.profile_service import getFullName

dashboard_temp_name = "dashboard/dashboard.html"
expense_temp_name = "dashboard/office_expense_dashboard.html"
expense_record_temp_name = "dashboard/office_expense_record.html"
category_temp_name = "dashboard/office_expense_category.html"
diesel_temp_name = "dashboard/office_expense_diesel.html"
electricity_temp_name = "dashboard/office_expense_electricity.html"

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
        name = request.user.first_name+" "+request.user.last_name
        now = timezone.localtime()
        total_ekedc = totalMonthlyPrepaid(ekedcQuerySet())
        total_diesel = totalMonthlyDiesel(dieselQueryset())
        total_expenses = totalMonthlyExpenses(expenseQueryset())
        yearly_ekdc = totalAnnualPrepaid(ekedcQuerySet())
        yearly_diesel = totalAnnualDiesel(dieselQueryset())
        yearly_expenses = totalAnnualExpenses(expenseQueryset())
        monthly_expenses = total_ekedc+total_diesel+total_expenses
        yearly_expenses = yearly_ekdc+yearly_diesel+yearly_expenses
        return render(
            request, dashboard_temp_name,
            context={
                "greet":get_greeting(), 
                "user_name":name, "now":now,
                "monthly_expenditure": monthly_expenses,
                "yearly_expenditure": yearly_expenses,
                "total_diesel":total_diesel,
                "total_ekedc":total_ekedc,
                "total_expenses": total_expenses,
                "user_name":getFullName(request)
            }
        )
    
    def post(self, request):
        return render(request, dashboard_temp_name)

@method_decorator(login_required, name="dispatch") 
class OfficeExpenseDashboard(View):
    def get(self, request):
        return render(
            request, 
            expense_temp_name,
            {"user_name":request.user.first_name[0]+request.user.last_name[0]}

        )

@method_decorator(login_required, name="dispatch")
class OfficeExpenseCategory(View):
    def get(self, request):
        return render(
            request, 
            category_temp_name,
            {"user_name":request.user.first_name[0]+request.user.last_name[0]}
        )   


