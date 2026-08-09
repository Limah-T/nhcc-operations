from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import DatabaseError
from django.contrib import messages
from django.views import View
from django import forms
from account.services.profile_service import getNameAvatar
from core.forms import FilterDateForm
from core.utils.helper_functions import set_date
from core.utils.error_responses import (
    EXPENSE_404, EXPENSES_404, SERVER_ERROR, 
    NOTHING_TO_UPDATE, QUEUE_ERROR)
from core.utils.custom_exceptions import NothingToUpdateError
from core.utils.success_responses import (
    EXPENSE_CREATED, EXPENSES_CREATED, EXPENSE_UPDATED, 
    EXPENSE_DELETED, EXPENSES_DELETED)
from dashboard.views import expense_record_temp_name, expense_temp_name
from ..services.expense_service import (
    ExpensePayloadParser, expense_context_data, 
    ExpenseDataInserter, ExpenseDataUpdater, ExpenseDataDeleter
)
from ..forms import ExpenseForm
from ..models import Expense

expense_url_name = "expenses"

def error_response(request, code:int):
    start_date, end_date = set_date()
    return render(
        request=request, template_name=expense_record_temp_name,
        context=expense_context_data(request.user, start_date, end_date),
        status=code
    )
   
@login_required
def expenseOverview(request):
    return render(
        request=request, 
        template_name=expense_temp_name,
        context={"user_name":getNameAvatar(request.user)}

    )

@method_decorator(login_required, "dispatch")
class ExpenseGetCreateView(View):

    def get(self, request):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        form = FilterDateForm(
            data={"start_date":start_date, "end_date":end_date}
        )
        if form.is_valid():
            try:
                start_date = form.cleaned_data["start_date"]
                end_date = form.cleaned_data["end_date"]  
                return render(
                    request=request, template_name=expense_record_temp_name,
                    context = expense_context_data(request.user, start_date, end_date),
                    status=200
                )         
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else:
            code = 400
            messages.error(request, form.errors)
        start_date, end_date = set_date()
        return render(
            request=request, 
            template_name=expense_record_temp_name,
            context=expense_context_data(request.user, start_date, end_date, form),
            status=code
        )

    def _single_handler(self, request):
        field_data = ExpensePayloadParser(request).parse_single()
        
        form = ExpenseForm(data=field_data)
        if form.is_valid():
            try:
                expense = ExpenseDataInserter(form.cleaned_data, request.user)
                expense.create_single()
                messages.success(request, EXPENSE_CREATED)
                return redirect(expense_url_name)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else:
            code = 400
            messages.error(request, form.errors)

        return error_response(request, code)

    def _bulk_handler(self, request):
        field_data = ExpensePayloadParser(request).parse_bulk()
        expense_list = []
        for category, name, amount, quantity, date in zip(
                field_data["category"], field_data["name"],
                field_data["amount"], field_data["quantity"],
                field_data["date"]
            ):
            form = ExpenseForm(data={
                    "category":category,
                    "name":name, "amount":amount,
                    "quantity":quantity, "date":date
                })
            if not form.is_valid():
               messages.error(request, form.errors)
               return error_response(request, code=400)
            expense_list.append(form.cleaned_data)
        try:
            expense = ExpenseDataInserter(expense_list, request.user)
            expense.create_bulk()
            messages.success(request, EXPENSES_CREATED)
            return redirect(expense_url_name)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)

        return error_response(request, code)

    def post(self, request) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
           return self._single_handler(request)
        elif action == "bulk":
            return self._bulk_handler(request)
        
        else: return redirect(expense_url_name)

@method_decorator(login_required, "dispatch")
class ExpenseUpdateView(View):
    def get(self, request, id=None):
        return redirect(expense_url_name)

    def _single_handler(self, request, id):
        field_data = ExpensePayloadParser(request).parse_single()
        form = ExpenseForm(data=field_data)
        if form.is_valid():
            try:
                expense = ExpenseDataUpdater(form.cleaned_data, request.user)
                expense.update_single(id)
                messages.success(request, EXPENSE_UPDATED)
                return redirect(expense_url_name)
            except Expense.DoesNotExist:
                code = 404
                messages.error(request, EXPENSES_404)
            except NothingToUpdateError:
                code = 400
                messages.error(request, NOTHING_TO_UPDATE)
            except DatabaseError:
                code = 400
                messages.error(request, QUEUE_ERROR)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else:
            code = 400
            messages.error(request, form.errors)

        return error_response(request, code)

    def post(self, request, id=None) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
           return self._single_handler(request, id)

        return redirect(expense_url_name)
    
@method_decorator(login_required, "dispatch")
class ExpenseDeleteView(View):
    def get(self, request, id=None):
       return redirect(expense_url_name)

    def _single_handler(self, request, id:int):        
        try:
            ExpenseDataDeleter().delete_single(id)
            messages.success(request, EXPENSE_DELETED)
            return redirect(expense_url_name)
        except Expense.DoesNotExist:
            code = 404
            messages.error(request, EXPENSE_404)
        except DatabaseError:
            code = 400
            messages.error(request, QUEUE_ERROR)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)

        return error_response(request, code)

    def _bulk_handler(self, request, expense_ids:list):
        try:
            if expense_ids:
                ExpenseDataDeleter().delete_bulk(expense_ids)
                messages.success(request, EXPENSES_DELETED)
            return redirect(expense_url_name)
        except Expense.DoesNotExist:
            code = 404
            messages.error(request, EXPENSES_404)
        except DatabaseError:
            code = 400
            messages.error(request, QUEUE_ERROR)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)
            
        return error_response(request, code)

    def post(self, request, id=None) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
            return self._single_handler(request, id)
        elif action == "bulk":
            expense_ids = request.POST.getlist("expense_ids")
            return self._bulk_handler(request, expense_ids)

        return redirect(expense_url_name)