from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from decimal import Decimal
from nhcc_operations.services.generic_service import diesel_404
from dashboard.views import diesel_temp_name
from nhcc_operations.services.http_response_services import (
    error_response, success_response
)
from ..services.diesel_service import (
    DieselPayloadParser, diesel_context_data,
    create_single, create_bulk, update_single, 
    delete_single, delete_bulk
)
from ..forms import DieselForm

diesel_url_name = "diesel"

@login_required
def dieselOverView(request):
    return render(
        request=request, 
        template_name=diesel_temp_name,
        context=diesel_context_data(request.user),
        status=200
    )

@method_decorator(login_required, "dispatch")
class DieselManagementView(View):

    def get(self, request):
        return render(
            request=request, 
            template_name=diesel_temp_name,
            context=diesel_context_data(request.user),
            status=200
        )

    def _handle_single_action(self, request):
        """Orchestrates single workflow"""
        field_data = DieselPayloadParser(request).parse_single()
        form = DieselForm(data=field_data)
        if form.is_valid():
            error = create_single(form.cleaned_data, request.user)
            if error is None:
                message = "Diesel record created successfully."
                return success_response(request, diesel_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = form.errors, 400
        return error_response(
            request=request, 
            template=diesel_temp_name, 
            context=diesel_context_data(request.user),
            message=message,
            status_code=code
        )
    
    def _handle_bulk_action(self, request):
        """Orchestrates bulk workflow"""
        field_data = DieselPayloadParser(request).parse_bulk()
        diesel_list = []
        can_proceed = True
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
                message, code = form.errors, 400
                can_proceed = False
                break
            diesel_list.append(form.cleaned_data)

        if can_proceed:
            error = create_bulk(diesel_list, request.user)
            if error is None:
                message = "Diesel records created successfully."
                return success_response(request, diesel_url_name, message)
            else: 
                message, code = error[0], error[1]
        
        return error_response(
            request, diesel_temp_name, 
            diesel_context_data(request.user), 
            message, code
        )
    
    def post(self, request) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
            return self._handle_single_action(request)
        
        return self._handle_bulk_action(request)
        
@method_decorator(login_required, "dispatch")
class DieselUpdateView(View):
    def get(self, request, pk=None):
        return redirect(diesel_url_name)

    def _handle_single_action(self, request, id):
        """Orchestrates a single workflow"""

        field_data = DieselPayloadParser(request).parse_single()
        transport = field_data["transport"] 
        field_data["transport"] = Decimal(transport.replace(",", ""))
        form = DieselForm(data=field_data)
        if form.is_valid():
            error = update_single(id, form.cleaned_data, request.user)
            if error is None:
                message = "Diesel record updated successfully."
                return success_response(request, diesel_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = form.errors, 400
        return error_response(
            request, diesel_temp_name, 
            diesel_context_data(request.user), 
            message, code
        )

    def post(self, request, pk=None):
        action = request.POST.get("action")
        if action == "single":
           
           return self._handle_single_action(request, pk)

        return success_response(request, diesel_url_name, None)
    
class DieselDeleteView(View):
    def get(self, request):
       return success_response(request, diesel_url_name, None)

    def _handle_single_action(self, request, pk:int):
        """Orchestrates a single workflow"""
        
        error = delete_single(pk)
        if error is None:
            message = "Diesel record deleted successfully."
            return success_response(request, diesel_url_name, message)
        
        message, code = error[0], error[1]
        return error_response(
            request, diesel_temp_name, 
            diesel_context_data(request.user), 
            message, code
        )

    def _handle_bulk_action(self, request, diesel_ids:list):
        """Orchestrates bulk workflow"""
        if diesel_ids:
            error = delete_bulk(diesel_ids)
            if error is None:
                message = "Diesel records deleted successfully"
                return success_response(request, diesel_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = diesel_404, 400
        return error_response(
            request, diesel_temp_name, 
            diesel_context_data(request.user), 
            message, code
        )

    def post(self, request, pk=None) -> HttpResponse:
        action = request.POST.get("action")
        if action == "single":
            return self._handle_single_action(request, pk)
        
        diesel_ids = request.POST.getlist("diesel_ids")
        return self._handle_bulk_action(request, diesel_ids)

