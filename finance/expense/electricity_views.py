from django.shortcuts import render
from django.views import View
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from decimal import Decimal
from dashboard.views import electricity_temp_name
from nhcc_operations.services.generic_service import ekedc_404
from nhcc_operations.services.http_response_services import (
    error_response, success_response
)
from .services.electricity_service import (
    EkedcPayloadParser, ekedc_context_data,
    create_single, create_bulk, update_single,
    delete_single, delete_bulk, 
)
from .forms import ElectricityForm

ekedc_url_name = "ekedc"

@login_required
def ekedcOverview(request):
    return render(
        request=request, 
        template_name=electricity_temp_name,
        context=ekedc_context_data(request.user)
    ) 

@method_decorator(login_required, name="dispatch")
class EkedcManagementView(View):
    def get(self, request):  
        return render(
            request=request,
            template_name=electricity_temp_name,
            context=ekedc_context_data(request.user),
            status=200
        )
    def _handle_single_action(self, request):
        """Orchestrates single workflow"""
        field_data = EkedcPayloadParser(request).parse_single()
        form = ElectricityForm(data=field_data)
        if form.is_valid():
            error = create_single(form.cleaned_data, request.user)
            if error is None:
                message = "Ekedc record created successfully."
                return success_response(request, ekedc_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = form.errors, 400
        return error_response(
            request=request, 
            template=electricity_temp_name, 
            context=ekedc_context_data(request.user),
            message=message,
            status_code=code
        )
    
    def _handle_bulk_action(self, request):
        """Orchestrates bulk workflow"""
        field_data = EkedcPayloadParser(request).parse_bulk()
        ekedc_list = []
        can_proceed = True
        for kwh, amount, date in zip(
            field_data["kwh"], field_data["amount"], field_data["date"],
        ):
            form = ElectricityForm(
                data={"kwh":kwh, "amount":amount, "date":date})
            if not form.is_valid():
                message, code = form.errors, 400
                can_proceed = False
                break
            ekedc_list.append(form.cleaned_data)

        if can_proceed:
            error = create_bulk(ekedc_list, request.user)
            if error is None:
                message = "Ekedc records created successfully."
                return success_response(request, ekedc_url_name, message)
            else: 
                message, code = error[0], error[1]
        
        return error_response(
            request, electricity_temp_name, 
            ekedc_context_data(request.user), 
            message, code
        )

    def post(self, request) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
            return self._handle_single_action(request)
        
        return self._handle_bulk_action(request)
    

@method_decorator(login_required, "dispatch")
class EkedcUpdateView(View):
    def get(self, request, pk=None):
        return success_response(request, ekedc_url_name, None)

    def _handle_single_action(self, request, id):
        """Orchestrates a single workflow"""

        field_data = EkedcPayloadParser(request).parse_single()
        amount = field_data["amount"] 
        field_data["amount"] = Decimal(amount.replace(",", ""))
        form = ElectricityForm(data=field_data)
        if form.is_valid():
            error = update_single(id, form.cleaned_data, request.user)
            if error is None:
                message = "Ekedc record updated successfully."
                return success_response(request, ekedc_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = form.errors, 400
        return error_response(
            request, electricity_temp_name, 
            ekedc_context_data(request.user), 
            message, code
        )

    def post(self, request, pk=None):
        action = request.POST.get("action")
        if action == "single":
           
           return self._handle_single_action(request, pk)

        return success_response(request, ekedc_url_name, None)


class EkedcDeleteView(View):
    def get(self, request):
       return success_response(request, ekedc_url_name, None)

    def _handle_single_action(self, request, pk:int):
        """Orchestrates a single workflow"""
        
        error = delete_single(pk)
        if error is None:
            message = "Ekedc record deleted successfully."
            return success_response(request, ekedc_url_name, message)
        
        message, code = error[0], error[1]
        return error_response(
            request, electricity_temp_name, 
            ekedc_context_data(request.user), 
            message, code
        )

    def _handle_bulk_action(self, request, ekedc_ids:list):
        """Orchestrates bulk workflow"""
        if ekedc_ids:
            error = delete_bulk(ekedc_ids)
            if error is None:
                message = "Ekedc records deleted successfully"
                return success_response(request, ekedc_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = ekedc_404, 400
        return error_response(
            request, electricity_temp_name, 
            ekedc_context_data(request.user), 
            message, code
        )

    def post(self, request, pk=None) -> HttpResponse:
        action = request.POST.get("action")
        if action == "single":
            return self._handle_single_action(request, pk)
        
        ekedc_ids = request.POST.getlist("ekedc_ids")
        return self._handle_bulk_action(request, ekedc_ids)
