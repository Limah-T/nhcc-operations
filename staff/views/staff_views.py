from django.shortcuts import render, redirect
from django.views import View
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import IntegrityError, DatabaseError
from django.views import View
from django.contrib import messages
from decimal import Decimal
from dashboard.views import staff_account_temp_name
from core.utils.custom_exceptions import NothingToUpdateError
from core.utils.error_responses import (
    STAFF_404, STAFFS_404, SERVER_ERROR, QUEUE_ERROR, 
    STAFF_CREDENTIAL_ERROR, NOTHING_TO_UPDATE)
from core.utils.success_responses import (
    STAFF_CREATED, STAFFS_CREATED, STAFF_UPDATED, 
    STAFF_DELETED, STAFFS_DELETED)
from ..services.staff_service import (
    StaffPayloadParser, staff_context_data, 
    StaffDataInserter, StaffDataUpdater, StaffDataDeleter)
from ..forms import StaffForm
from ..models import Staff

staff_url_name = "staff"

def error_response(request, code:int):
    return render(
        request=request, 
        template_name=staff_account_temp_name, 
        context=staff_context_data(request.user), 
        status=code
    )

@method_decorator(login_required, "dispatch")
class StaffGetCreateView(View):

    def get(self, request):
        return render(
            request=request, 
            template_name=staff_account_temp_name,
            context=staff_context_data(request.user),
            status=200
        )

    def _single_handler(self, request):
        field_data = StaffPayloadParser(request).parse_single()
        form = StaffForm(data=field_data)
        if form.is_valid():
            try:
                staff = StaffDataInserter(form.cleaned_data, request.user)
                staff.create_single()
                messages.success(request, STAFF_CREATED)
                return redirect(staff_url_name)
            except IntegrityError:
                code = 400
                messages.error(request, STAFF_CREDENTIAL_ERROR)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else: 
            code = 400
            messages.error(request, form.errors)

        return error_response(request, code)
    
    def _bulk_handler(self, request):
        field_data = StaffPayloadParser(request).parse_bulk()
        staff_list = []
        for role, first_name, last_name, email,\
            phone_number, salary, bank_name, \
            account_name, account_number, employment_date\
                in zip(
                field_data["role"], field_data["first_name"],
                field_data["last_name"], field_data["email"],
                field_data["phone_number"], field_data["salary"],
                field_data["bank_name"], field_data["account_name"],
                field_data["account_number"], field_data["employment_date"]
            ):
            form = StaffForm(data={
                "role": role, "first_name":first_name,
                "last_name":last_name, "email":email,
                "phone_number":phone_number, "salary":salary,
                "bank_name":bank_name,
                "account_name":account_name,
                "account_number":account_number,
                "employment_date": employment_date
            })
            if not form.is_valid():
                messages.error(request, form.errors)
                return error_response(request, code=400)
            staff_list.append(form.cleaned_data)

        try:
            staff = StaffDataInserter(staff_list, request.user)
            staff.create_bulk()
            messages.success(request, STAFFS_CREATED)
            return redirect(staff_url_name)
        except IntegrityError:
            code = 400
            messages.error(request, STAFF_CREDENTIAL_ERROR)
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

        return redirect(staff_url_name)
        
@method_decorator(login_required, "dispatch")
class StaffUpdateView(View):
    def get(self, request, id=None):
        return redirect(staff_url_name)

    def _single_handler(self, request, id):
        field_data = StaffPayloadParser(request).parse_single()
        amount = field_data["salary"]
        field_data["salary"] = Decimal(amount.replace(",", ""))
        form = StaffForm(data=field_data)
        if form.is_valid():
            try:
                staff = StaffDataUpdater(form.cleaned_data, request.user)
                staff.update_single(id)
                messages.success(request, STAFF_UPDATED)
                return redirect(staff_url_name)
            except Staff.DoesNotExist:
                code = 404
                messages.error(request, STAFF_404)
            except NothingToUpdateError:
                code = 400
                messages.error(request, NOTHING_TO_UPDATE)
            except IntegrityError:
                code = 400
                messages.error(request, STAFF_CREDENTIAL_ERROR)
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

        return redirect(staff_url_name)
    
class StaffDeleteView(View):
    def get(self, request, id=None):
       return redirect(staff_url_name)

    def _single_handler(self, request, id:int):
        try:
            StaffDataDeleter().delete_single(id)
            messages.success(request, STAFF_DELETED)
            return redirect(staff_url_name)
        except Staff.DoesNotExist:
            code = 404
            messages.error(request, STAFF_404)
        except DatabaseError:
            code = 400
            messages.error(request, QUEUE_ERROR)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)

        return error_response(request, code)

    def _bulk_handler(self, request, staff_ids:list):
        try:
            if staff_ids:
                StaffDataDeleter().delete_bulk(staff_ids)
                messages.success(request, STAFFS_DELETED)
            return redirect(staff_url_name)
        except Staff.DoesNotExist:
            code = 404
            messages.error(request, STAFFS_404)
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
            staff_ids = request.POST.getlist("staff_ids")
            return self._bulk_handler(request, staff_ids)
        
        return redirect(staff_url_name)
    