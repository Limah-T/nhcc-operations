from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.db import DatabaseError
from django import forms
from decimal import Decimal
from django.contrib import messages
from dashboard.views import diesel_temp_name
from core.utils.helper_functions import set_date
from core.utils.error_responses import (
    DIESEL_404, DIESELS_404, SERVER_ERROR, NOTHING_TO_UPDATE, QUEUE_ERROR)
from core.utils.custom_exceptions import NothingToUpdateError
from core.utils.success_responses import (
    DIESEL_CREATED, DIESELS_CREATED, DIESEL_UPDATED, DIESEL_DELETED, DIESELS_DELETED)
from core.forms import FilterDateForm
from ..services.diesel_service import (
    DieselPayloadParser, diesel_context_data,
    DieselDataInserter, DieselDataUpdater, DieselDataDeleter)
from ..forms import DieselForm
from ..models import Diesel

diesel_url_name = "diesel"

def error_response(request, code:int):
    start_date, end_date = set_date()
    return render(
        request=request, template_name=diesel_temp_name,
        context=diesel_context_data(request.user, start_date, end_date),
        status=code
    )

@method_decorator(login_required, "dispatch")
class DieselGetCreateView(View):

    def get(self, request, id=None):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        try:
            form = FilterDateForm(data={
                "start_date":start_date, "end_date":end_date
            })
            if not form.is_valid():
                raise forms.ValidationError
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            code = 200
        except forms.ValidationError:
            code = 400
            messages.error(request, form.errors)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)
        return render(
            request=request, template_name=diesel_temp_name,
            context=diesel_context_data(request.user, start_date, end_date),
            status=code
        )

    def _single_handler(self, request):
        field_data = DieselPayloadParser(request).parse_single()
        form = DieselForm(data=field_data)
        if form.is_valid():
            try:
                diesel = DieselDataInserter(form.cleaned_data, request.user)
                diesel.create_single()
                messages.success(request, DIESEL_CREATED)
                return redirect(diesel_url_name)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else:
            code = 400
            messages.error(request, form.errors)    
        return error_response(request, code)
    
    def _bulk_handler(self, request):
        field_data = DieselPayloadParser(request).parse_bulk()
        diesel_list = []
        for litres, price, supplier_name, transport, date in zip(
            field_data["litres"], field_data["price"], 
            field_data["supplier_name"],
            field_data["transport"], field_data["date"]
        ):
            form = DieselForm(
                data={
                    "litres": litres, "price": price,
                    "supplier_name": supplier_name,
                    "transport": transport, "date": date
                })
            if not form.is_valid():
                messages.error(request, form.errors)
                return error_response(request, code=400)
            diesel_list.append(form.cleaned_data)

        try:
            diesel = DieselDataInserter(diesel_list, request.user)
            diesel.create_bulk()
            messages.success(request, DIESELS_CREATED)
        except Exception:
            messages.error(request, SERVER_ERROR)   
            return error_response(request, code=500)
        return redirect(diesel_url_name)
    
    def post(self, request) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
            return self._single_handler(request)
        elif action == "bulk":
            return self._bulk_handler(request)
        
        return redirect(diesel_url_name)
        
@method_decorator(login_required, "dispatch")
class DieselUpdateView(View):
    def get(self, request, id=None):
        return redirect(diesel_url_name)

    def _single_handler(self, request, id):
        field_data = DieselPayloadParser(request).parse_single()
        transport = field_data["transport"] 
        field_data["transport"] = Decimal(transport.replace(",", ""))
        form = DieselForm(data=field_data)
        if form.is_valid():
            try:
                diesel = DieselDataUpdater(form.cleaned_data, request.user)
                diesel.update_single(id)
                messages.success(request, DIESEL_UPDATED)
                return redirect(diesel_url_name)
            except Diesel.DoesNotExist:
                code = 404
                messages.error(request, DIESEL_404)
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

        return redirect(diesel_url_name)
    
class DieselDeleteView(View):
    def get(self, request, id=None):
       return redirect(diesel_url_name)

    def _single_handler(self, request, id:int):        
        try:
            DieselDataDeleter().delete_single(id)
            messages.success(request, DIESEL_DELETED)
            return redirect(diesel_url_name)
        except Diesel.DoesNotExist:
            code = 404
            messages.error(request, DIESEL_404)
        except DatabaseError:
            code = 400
            messages.error(request, QUEUE_ERROR)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR) 

        return error_response(request, code)

    def _bulk_handler(self, request, diesel_ids:list):
        try:
            if diesel_ids:
                DieselDataDeleter().delete_bulk(diesel_ids)
                messages.success(request, DIESELS_DELETED)
            return redirect(diesel_url_name)
        except Diesel.DoesNotExist:
            code = 400
            messages.error(request, DIESELS_404)
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
            diesel_ids = request.POST.getlist("diesel_ids")
            return self._bulk_handler(request, diesel_ids)

        return redirect(diesel_url_name)

