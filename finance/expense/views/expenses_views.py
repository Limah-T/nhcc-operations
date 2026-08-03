from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from account.services.profile_service import getNameAvatar
from nhcc_operations.services.generic_service import empty_fields_error
from nhcc_operations.services.http_response_services import (
    error_response, success_response
)
from core.forms import DateForm
from dashboard.views import expense_record_temp_name, expense_temp_name
from ..services.expense_service import (
    ExpensePayloadParser,
    expense_context_data, 
    create_single, create_bulk,
    update_single, delete_single, 
    delete_bulk, date_constructor
)
from ..forms import ExpenseForm

expense_url_name = "expenses"

   
@login_required
def expenseOverview(request):
    return render(
        request=request, 
        template_name=expense_temp_name,
        context={"user_name":getNameAvatar(request.user)}

    )

@login_required
def expenseFilter(request):
    print(request)
    return redirect(expense_url_name)

@method_decorator(login_required, "dispatch")
class ExpenseManagementView(View):

    def get(self, request):
        print("IN MANAGEMENT")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        print(start_date, end_date)
        form = DateForm(data={"start_date":start_date, "end_date":end_date})
        if form.is_valid():
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            
        return render(
            request=request, 
            template_name=expense_record_temp_name,
            context=expense_context_data(request.user, start_date, end_date),
            status=200
        )

    def _handle_single_action(self, request):
        """Orchestrates single workflow"""
        field_data = ExpensePayloadParser(request).parse_single()
        
        form = ExpenseForm(data=field_data)
        if form.is_valid():
            error = create_single(form.cleaned_data, request.user)
            if error is None:
                message = "Expense created successfully."
                return success_response(request, expense_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = form.errors, 400
        return error_response(
            request, expense_record_temp_name, 
            expense_context_data(request.user), message, code
        )

    def _handle_bulk_action(self, request):
        """Orchestrates bulk workflow"""
        field_data = ExpensePayloadParser(request).parse_bulk()
        expense_list = []
        can_proceed = True

        for category, name, amount, quantity, date in zip(
                field_data["category"], field_data["name"],
                field_data["amount"], field_data["quantity"],
                field_data["date"]
            ):
            form = ExpenseForm(data={
                    "category":category,
                    "name":name, "amount":amount,
                    "quantity":quantity, "date":date
                }
            )
            if not form.is_valid():
               message, code = form.errors, 400
               can_proceed = False
               break
            expense_list.append(form.cleaned_data)
        if can_proceed:
            error = create_bulk(expense_list, request.user)
            if error is None:
                message = "Expenses created successfully."
                return success_response(request, expense_url_name, message)
            else: 
                message, code = error[0], error[1]

        return error_response(
            request, expense_record_temp_name, 
            expense_context_data(request.user), message, code
        )

    def post(self, request) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
           return self._handle_single_action(request)
        
        return self._handle_bulk_action(request)

@method_decorator(login_required, "dispatch")
class ExpenseUpdateView(View):
    def get(self, request, pk=None):
        return success_response(request, expense_url_name, None)

    def _handle_single_action(self, request, id):
        """Orchestrates a single workflow"""

        field_data = ExpensePayloadParser(request).parse_single()
        form = ExpenseForm(data=field_data)
        if form.is_valid():
            error = update_single(id, form.cleaned_data, request.user)
            if error is None:
                message = "Expense updated successfully."
                return success_response(request, expense_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = form.errors, 400
        return error_response(
            request, expense_record_temp_name, 
            expense_context_data(request.user), message, code
        )

    def post(self, request, pk=None):
        action = request.POST.get("action")
        if action == "single":
           
           return self._handle_single_action(request, pk)

        return success_response(request, expense_url_name, None)
    
@method_decorator(login_required, "dispatch")
class ExpenseDeleteView(View):
    def get(self, request):
       return success_response(request, expense_url_name, None)

    def _handle_single_action(self, request, pk:int):
        """Orchestrates a single workflow"""
        
        error = delete_single(pk)
        if error is None:
            message = "Expense deleted successfully."
            return success_response(request, expense_url_name, message)
        
        message, code = error[0], error[1]
        return error_response(
            request, expense_record_temp_name, 
            expense_context_data(request.user), message, code
        )

    def _handle_bulk_action(self, request, expense_ids:list):
        """Orchestrates bulk workflow"""
        if expense_ids:
            error = delete_bulk(expense_ids)
            if error is None:
                message = "Expenses deleted successfully"
                return success_response(request, expense_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = empty_fields_error, 400
        return error_response(
            request, expense_record_temp_name, 
            expense_context_data(request.user), message, code
        )

    def post(self, request, pk=None) -> HttpResponse:
        action = request.POST.get("action")
        if action == "single":
            return self._handle_single_action(request, pk)
        
        expense_ids = request.POST.getlist("expense_ids")
        return self._handle_bulk_action(request, expense_ids)