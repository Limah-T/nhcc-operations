from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from account.services.profile_service import getFullName
from nhcc_operations.services.generic_service import expense_404
from dashboard.views import expense_record_temp_name
from nhcc_operations.services.generic_service import (
    intId, emptyFields
)
from .services.expense_service import (
    expenseQueryset, expenseRetrieval, 
    expenseFormValidator, totalMonthlyExpenses,
    processCreate, create, update,
    delete_one, delete_many
)
from .services.category_service import categoryQueryset
from .forms import ExpenseForm

url_name = "expenses"

def expense_context_data(request, error_message):
    categories = categoryQueryset()
    queryset = expenseQueryset()
    total = totalMonthlyExpenses(queryset)
    return {
        "categories":categories,
        "expenses":queryset,
        "count":queryset.count(),
        "monthly_total_display": f"₦{total:,.2f}",
        "errors":error_message,
        "user_name":getFullName(request),
    }

@method_decorator(login_required, "dispatch")
class ExpenseView(View):
    def get(self, request):
        
        return render(
            request, expense_record_temp_name,
            context=expense_context_data(request, error_message=None),
            status=200
        )

    def post(self, request):
        categories = request.POST.getlist("category", [])
        names = request.POST.getlist("name", [])
        amounts = request.POST.getlist("amount", [])
        quantities = request.POST.getlist("quantity", [])
        dates = request.POST.getlist("date", [])

        if not emptyFields([
            categories, names, amounts, quantities
        ]):
            response = processCreate(
                categories, names, amounts, 
                quantities, dates,
                request.user, getFullName(request)
            )
            if not isinstance(response, ExpenseForm):
                error = create(response)
                if error is None:
                    return redirect(url_name) 
                message, code = {"Create Error": error["error"]}, error["status"]
            else: message, code = response.errors, 400
        else: 
            message, code = {"Empty Fields": ["All fields are empty"]}, 400
        return render(
            request, expense_record_temp_name,
            context=expense_context_data(request, error_message=message),
            status=code
        )
    
@login_required
def retrieve_expenses(request, pk):
    expense = expenseRetrieval(pk)
    if expense:
        return render(
            request, expense_record_temp_name,
            context={"expense":expense},
            status=200
        )
    message = {"Not Found": expense_404["error"]}
    code = expense_404["status"]
    return render(
        request, expense_record_temp_name,
        context=expense_context_data(request, error_message=message),
        status=code
    )

@login_required
def edit_expense(request, pk):
    if request.method != "POST":
        return redirect(url_name)
    
    if intId(pk):
        expense = expenseRetrieval(pk)
        if expense:
            category = request.POST.get("category", expense.category)
            name = request.POST.get("name", expense.name)
            quantity = request.POST.get("quantity", expense.quantity)
            amount = request.POST.get("amount", expense.amount)
            date = request.POST.get("date", expense.created_at.date)
            form = expenseFormValidator(
                category, name, amount, quantity, date,
                )
            if form.is_valid():
                error = update(
                    expense, category, name, quantity, 
                    amount, date, request.user, getFullName(request)
                )
                if error is None:
                    return redirect(url_name)
                message, code = {"Update Error": error["error"]}, error["status"]
            else: message, code = form.errors, 400
        else: message, code = {"Not found": expense_404["error"]}, expense_404["status"]
    else: message, code = {"Not found": expense_404["error"]}, expense_404["status"]
    return render(
        request, expense_record_temp_name,
        context=expense_context_data(request, error_message=message),
        status=code
    )

@login_required
def delete_expense(request, pk):
    if request.method != "POST":
        return redirect(url_name)
    
    if intId(pk):
        expense = expenseRetrieval(pk)
        if expense: 
            error = delete_one(expense)
            if error is None:
                return redirect(url_name)
            else:
                message, code = {"Delete Error": error["error"]}, error["status"]
        else: 
            message, code = {"Not Found": expense_404["error"]}, expense_404["status"]
    else: 
        message, code = {"Not Found": expense_404["error"]}, expense_404["status"]

    return render(
        request, expense_record_temp_name,
        expense_context_data(request, error_message=message),
        status=code
    )


@login_required
def delete_expenses(request):
    if request.method != "POST":
        return redirect(url_name)

    expense_ids = request.POST.getlist("expense_ids")
    print(expense_ids, "in views")
    if expense_ids:
        error = delete_many(expense_ids)
        if error is None:
            return redirect(url_name)
        else:
            message, code = {"Delete Error": error["error"]}, error["status"]
    else: 
        message, code = {"Not Found": expense_404["error"]}, expense_404["status"]

    return render(
        request, expense_record_temp_name,
        expense_context_data(request, error_message=message),
        status=code
    )