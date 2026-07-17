from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from finance.expense.models import EKEDC, Diesel, Expense

dashboard_temp_name = "dashboard/dashboard.html"
expense_temp_name = "dashboard/office_expense_dashboard.html"
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
        total_ekedc = sum(
            item.amount for item in EKEDC.objects.all() 
                if (item.created_at.year and item.created_at.month
                    ) == (now.year and now.month
                )
        )
        total_diesel = sum(
            item.total for item in Diesel.objects.all() 
                if (item.created_at.year and item.created_at.month
                    ) == (now.year and now.month
                )
        )
        yearly_ekdc = sum(
            item.amount for item in EKEDC.objects.all() 
                if (item.created_at.year == now.year)
        )
        yearly_diesel = sum(
            item.total for item in Diesel.objects.all() 
                if (item.created_at.year == now.year)
        )
        return render(
            request, dashboard_temp_name,
            context={
                "greet":get_greeting(), 
                "user_name":name, "now":now,
                "monthly_expenditure": total_ekedc+total_diesel,
                "yearly_expenditure": yearly_ekdc+yearly_diesel,
                "total_diesel":total_diesel,
                "total_ekedc":total_ekedc
            }
        )
    
    def post(self, request):
        return render(request, dashboard_temp_name)

@method_decorator(login_required, name="dispatch") 
class OfficeExpenseDashboard(View):
    def get(self, request):
        return render(
            request, expense_temp_name,
        )

@method_decorator(login_required, name="dispatch")
class OfficeExpenseCategory(View):
    def get(self, request):
        return render(
            request, category_temp_name
        )   


