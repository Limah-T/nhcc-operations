from django.shortcuts import render, redirect
from django.views import View
from django import forms
from django.contrib import messages
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import DatabaseError
from decimal import Decimal
from dashboard.views import electricity_temp_name
from core.utils.helper_functions import set_date
from core.utils.error_responses import (
    EKEDC_404, EKEDCS_404, SERVER_ERROR, NOTHING_TO_UPDATE, QUEUE_ERROR)
from core.utils.custom_exceptions import NothingToUpdateError
from core.utils.success_responses import (
    EKEDC_CREATED, EKEDCS_CREATED, EKEDC_UPDATED, EKEDC_DELETED, EKEDCS_DELETED)
from core.forms import FilterDateForm
from ..services.electricity_service import (
    EkedcPayloadParser, ekedc_context_data,
    EkedcDataInserter, EkedcDataUpdater, EkedcDataDeleter)
from ..forms import ElectricityForm
from ..models import EKEDC

def error_response(request, code:int):
    start_date, end_date = set_date()
    return render(
        request=request, template_name=electricity_temp_name,
        context=ekedc_context_data(request.user, start_date, end_date),
        status=code
    )

ekedc_url_name = "ekedc"

@method_decorator(login_required, name="dispatch")
class EkedcGetCreateView(View):
    def get(self, request, id=None):  
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        try:
            form = FilterDateForm(data={
                "start_date":start_date, "end_date":end_date})
            if not form.is_valid(): raise forms.ValidationError
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
            request=request, template_name=electricity_temp_name,
            context=ekedc_context_data(request.user, start_date, end_date),
            status=code
        )

    def _single_handler(self, request):
        field_data = EkedcPayloadParser(request).parse_single()
        form = ElectricityForm(data=field_data)
        if form.is_valid():
            try:
                ekedc = EkedcDataInserter(form.cleaned_data, request.user)
                ekedc.create_single()
                messages.success(request, EKEDC_CREATED)
                return redirect(ekedc_url_name)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else:
            code = 400
            messages.error(request, form.errors)    
        return error_response(request, code)

    def _bulk_handler(self, request):
        field_data = EkedcPayloadParser(request).parse_bulk()
        ekedc_list = []

        for kwh, amount, date in zip(
            field_data["kwh"], field_data["amount"], field_data["date"]
        ):
            form = ElectricityForm(
                data={"kwh":kwh, "amount":amount, "date":date})
            if not form.is_valid():
                messages.error(request, form.errors)
                return error_response(request, code=400)
            ekedc_list.append(form.cleaned_data)

        try:
            ekedc = EkedcDataInserter(ekedc_list, request.user)
            ekedc.create_bulk()
            messages.success(request, EKEDCS_CREATED)
        except Exception:
            messages.error(request, SERVER_ERROR)
            return error_response(request, code=500)
        return redirect(ekedc_url_name)

    def post(self, request) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
            return self._single_handler(request)
        elif action == "bulk":
            return self._bulk_handler(request)
        
        return redirect(ekedc_url_name)
    

@method_decorator(login_required, "dispatch")
class EkedcUpdateView(View):
    def get(self, request, id=None):
        return redirect(ekedc_url_name)

    def _single_handler(self, request, id):
        field_data = EkedcPayloadParser(request).parse_single()
        amount = field_data["amount"] 
        field_data["amount"] = Decimal(amount.replace(",", ""))
        form = ElectricityForm(data=field_data)
        if form.is_valid():
            try:
                ekedc = EkedcDataUpdater(form.cleaned_data, request.user)
                ekedc.update_single(id)
                messages.success(request, EKEDC_UPDATED)
                return redirect(ekedc_url_name)
            except EKEDC.DoesNotExist:
                code = 404
                messages.error(request, EKEDC_404)
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

        return redirect(ekedc_url_name)

class EkedcDeleteView(View):
    def get(self, request, id=None):
       return redirect(ekedc_url_name)

    def _single_handler(self, request, id:int): 
        try:
            EkedcDataDeleter().delete_single(id)
            messages.success(request, EKEDC_DELETED)
            return redirect(ekedc_url_name)
        except EKEDC.DoesNotExist:
            code = 404
            messages.error(request, EKEDC_404)
        except DatabaseError:
            code = 400
            messages.error(request, QUEUE_ERROR)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR) 

        return error_response(request, code)

    def _bulk_handler(self, request, ekedc_ids:list):  
        try:
            if ekedc_ids:
                EkedcDataDeleter().delete_bulk(ekedc_ids)
                messages.success(request, EKEDCS_DELETED)
            return redirect(ekedc_url_name)
        except EKEDC.DoesNotExist:
            code = 400
            messages.error(request, EKEDCS_404)
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
            ekedc_ids = request.POST.getlist("ekedc_ids")
            return self._bulk_handler(request, ekedc_ids)
        
        return redirect(ekedc_url_name)
