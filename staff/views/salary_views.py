from django.shortcuts import render, redirect
from django.views import View
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import DatabaseError
from django.views import View
from django.contrib import messages
from dashboard.views import salary_temp_name
from core.utils.custom_exceptions import NothingToUpdateError
from core.utils.error_responses import (
    SALARY_404, SALARIES_404, SERVER_ERROR, QUEUE_ERROR, NOTHING_TO_UPDATE)
from core.utils.success_responses import (
    SALARY_CREATED, SALARIES_CREATED, SALARY_UPDATED, 
    SALARY_DELETED, SALARIES_DELETED)
from core.forms import FilterDateForm
from core.utils.helper_functions import set_date
from ..services.salary_service import (
    SalaryPayloadParser, salary_context_data, 
    SalaryDataInserter, SalaryDataUpdater, SalaryDataDeleter)
from ..forms import SalaryForm
from ..models import StaffSalary

salary_url_name = "salaries"

def error_response(request, code:int):
    return render(
        request=request, 
        template_name=salary_temp_name, 
        context=salary_context_data(request.user), 
        status=code
    )

@method_decorator(login_required, "dispatch")
class SalaryGetCreateView(View):

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
                    request=request, template_name=salary_temp_name,
                    context = salary_context_data(request.user, start_date, end_date),
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
            template_name=salary_temp_name,
            context=salary_context_data(request.user, start_date, end_date),
            status=code
        )

    def _single_handler(self, request):
        field_data = SalaryPayloadParser(request).parse_single()
        form = SalaryForm(data=field_data)
        if form.is_valid():
            try:
                salary = SalaryDataInserter(form.cleaned_data, request.user)
                salary.create_single()
                messages.success(request, SALARY_CREATED)
                return redirect(salary_url_name)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else: 
            code = 400
            messages.error(request, form.errors)

        return error_response(request, code)
    
    def _bulk_handler(self, request):
        field_data = SalaryPayloadParser(request).parse_bulk()
        salary_list = []
        for staff, amount_paid, additional_info, date_received,\
                in zip(
                field_data["staff"], field_data["amount_paid"],
                field_data["additional_info"], field_data["date_received"],
            ):
            form = SalaryForm(data={
                "staff": staff, 
                "amount_paid":amount_paid,
                "additional_info":additional_info,
                "date_received": date_received
            })
            if not form.is_valid():
                messages.error(request, form.errors)
                return error_response(request, code=400)
            salary_list.append(form.cleaned_data)

        try:
            salary = SalaryDataInserter(salary_list, request.user)
            salary.create_bulk()
            messages.success(request, SALARIES_CREATED)
            return redirect(salary_url_name)
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

        return redirect(salary_url_name)
        
@method_decorator(login_required, "dispatch")
class SalaryUpdateView(View):
    def get(self, request, id=None):
        return redirect(salary_url_name)

    def _single_handler(self, request, id):
        field_data = SalaryPayloadParser(request).parse_single()
        form = SalaryForm(data=field_data)
        if form.is_valid():
            try:
                salary = SalaryDataUpdater(form.cleaned_data, request.user)
                salary.update_single(id)
                messages.success(request, SALARY_UPDATED)
                return redirect(salary_url_name)
            except StaffSalary.DoesNotExist:
                code = 404
                messages.error(request, SALARY_404)
            except NothingToUpdateError:
                code = 400
                messages.error(request, NOTHING_TO_UPDATE)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else: 
            code = 400
            messages.error(request, form.errors)
        return error_response(request, code)

    def post(self, request, id=None):
        action = request.POST.get("action")

        if action == "single":
           return self._single_handler(request, id)

        return redirect(salary_url_name)
    
class SalaryDeleteView(View):
    def get(self, request, id=None):
       return redirect(salary_url_name)

    def _single_handler(self, request, id:int):
        try:
            SalaryDataDeleter().delete_single(id)
            messages.success(request, SALARY_DELETED)
            return redirect(salary_url_name)
        except StaffSalary.DoesNotExist:
            code = 404
            messages.error(request, SALARY_404)
        except DatabaseError:
            code = 400
            messages.error(request, QUEUE_ERROR)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)

        return error_response(request, code)

    def _bulk_handler(self, request, salary_ids:list):
        try:
            if salary_ids:
                SalaryDataDeleter().delete_bulk(salary_ids)
                messages.success(request, SALARIES_DELETED)
            return redirect(salary_url_name)
        except StaffSalary.DoesNotExist:
            code = 404
            messages.error(request, SALARIES_404)
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
        if action == "bulk":
            salary_ids = request.POST.getlist("salary_ids")
            return self._bulk_handler(request, salary_ids)
        
        return redirect(salary_url_name)
    