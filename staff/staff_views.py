from django.shortcuts import render, redirect
from django.views import View
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from dashboard.views import staff_account_temp_name
from decimal import Decimal
from .services.staff_service import (
    StaffPayloadParser, 
    staff_context_data, create_single,
    create_bulk, update_single, 
    delete_single, delete_bulk
)
from nhcc_operations.services.generic_service import staff_404
from nhcc_operations.services.http_response_services import (
    success_response, error_response
)
from .forms import StaffForm

staff_url_name = "staff_records"

@method_decorator(login_required, "dispatch")
class StaffManagementView(View):

    def get(self, request):
        return render(
            request=request, 
            template_name=staff_account_temp_name,
            context=staff_context_data(request.user),
            status=200
        )

    def _handle_single_action(self, request):
        """Orchestrates single workflow"""
        field_data = StaffPayloadParser(request).parse_single()
        form = StaffForm(data=field_data)
        if form.is_valid():
            error = create_single(form.cleaned_data, request.user)
            if error is None:
                message = "Staff record created successfully."
                return success_response(request, staff_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = form.errors, 400
        return error_response(
            request=request, 
            template=staff_account_temp_name, 
            context=staff_context_data(request.user),
            message=message,
            status_code=code
        )
    
    def _handle_bulk_action(self, request):
        """Orchestrates bulk workflow"""
        field_data = StaffPayloadParser(request).parse_bulk()
        staff_list, can_proceed = [], True
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
                message, code = form.errors, 400
                can_proceed = False
                break

            staff_list.append(form.cleaned_data)
        if can_proceed:
            error = create_bulk(staff_list, request.user)
            if error is None:
                message = "Staff records created successfully."
                return success_response(request, staff_url_name, message)
            else: message, code = error[0], error[1]
        
        return error_response(
            request, staff_account_temp_name, 
            staff_context_data(request.user), 
            message, code
        )
    
    def post(self, request) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
            return self._handle_single_action(request)
        
        return self._handle_bulk_action(request)
        
@method_decorator(login_required, "dispatch")
class StaffUpdateView(View):
    def get(self, request, pk=None):
        return redirect(staff_url_name)

    def _handle_single_action(self, request, id):
        """Orchestrates a single workflow"""

        field_data = StaffPayloadParser(request).parse_single()

        amount = field_data["salary"]
        field_data["salary"] = Decimal(amount.replace(",", ""))
        form = StaffForm(data=field_data)
        if form.is_valid():
            error = update_single(id, form.cleaned_data, request.user)
            if error is None:
                message = "Staff record updated successfully."
                return success_response(request, staff_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = form.errors, 400
        return error_response(
            request, staff_account_temp_name, 
            staff_context_data(request.user), 
            message, code
        )

    def post(self, request, pk=None):
        action = request.POST.get("action")
        if action == "single":
           
           return self._handle_single_action(request, pk)

        return success_response(request, staff_url_name, None)
    
class StaffDeleteView(View):
    def get(self, request):
       return success_response(request, staff_url_name, None)

    def _handle_single_action(self, request, pk:int):
        """Orchestrates a single workflow"""
        
        error = delete_single(pk)
        if error is None:
            message = "Staff record deleted successfully."
            return success_response(request, staff_url_name, message)
        
        message, code = error[0], error[1]
        return error_response(
            request, staff_account_temp_name, 
            staff_context_data(request.user), 
            message, code
        )

    def _handle_bulk_action(self, request, staff_ids:list):
        """Orchestrates bulk workflow"""
        if staff_ids:
            error = delete_bulk(staff_ids)
            if error is None:
                message = "Role records deleted successfully"
                return success_response(request, staff_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = staff_404, 400
        return error_response(
            request, staff_account_temp_name, 
            staff_context_data(request.user), 
            message, code
        )

    def post(self, request, pk=None) -> HttpResponse:
        action = request.POST.get("action")
        
        if action == "single":
            return self._handle_single_action(request, pk)
        
        staff_ids = request.POST.getlist("staff_ids")
        return self._handle_bulk_action(request, staff_ids)
    