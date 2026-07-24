from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http.response import HttpResponse
from django.views import View
from dashboard.views import staff_account_temp_name
from nhcc_operations.services.http_response_services import (
    success_response, error_response
)
from .services.role_service import (
    RolePayloadParser,
    create_single, create_bulk,
    update_single,
    delete_single, delete_bulk
)
from .services.staff_service import staff_url_name, staff_context_data
from nhcc_operations.services.generic_service import role_404
from .forms import RoleForm


@method_decorator(login_required, "dispatch")
class RoleManagementView(View):

    def get(self, request):
        return render(
            request=request, 
            template_name=staff_account_temp_name,
            context=staff_context_data(request.user),
            status=200
        )

    def _handle_single_action(self, request):
        """Orchestrates single workflow"""
        field_data = RolePayloadParser(request).parse_single()
        form = RoleForm(data=field_data)
        if form.is_valid():
            error = create_single(form.cleaned_data, request.user)
            if error is None:
                message = "Role record created successfully."
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
        field_data = RolePayloadParser(request).parse_bulk()
        role_list = []
        can_proceed = True
        for name in field_data["name"]:
            form = RoleForm(data={"name":name})
            if not form.is_valid():
                message, code = form.errors, 400
                can_proceed = False
                break
            role_list.append(form.cleaned_data)

        if can_proceed:
            error = create_bulk(role_list, request.user)
            if error is None:
                message = "Role records created successfully."
                return success_response(request, staff_url_name, message)
            else: 
                message, code = error[0], error[1]
        
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
class RoleUpdateView(View):
    def get(self, request, pk=None):
        return redirect(staff_url_name)

    def _handle_single_action(self, request, id):
        """Orchestrates a single workflow"""

        field_data = RolePayloadParser(request).parse_single()
        form = RoleForm(data=field_data)
        if form.is_valid():
            error = update_single(id, form.cleaned_data, request.user)
            if error is None:
                message = "Role record updated successfully."
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
    
class RoleDeleteView(View):
    def get(self, request):
       return success_response(request, staff_url_name, None)

    def _handle_single_action(self, request, pk:int):
        """Orchestrates a single workflow"""
        
        error = delete_single(pk)
        if error is None:
            message = "Role record deleted successfully."
            return success_response(request, staff_url_name, message)
        
        message, code = error[0], error[1]
        return error_response(
            request, staff_account_temp_name, 
            staff_context_data(request.user), 
            message, code
        )

    def _handle_bulk_action(self, request, role_ids:list):
        """Orchestrates bulk workflow"""
        if role_ids:
            error = delete_bulk(role_ids)
            if error is None:
                message = "Role records deleted successfully"
                return success_response(request, staff_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = role_404, 400
        return error_response(
            request, staff_account_temp_name, 
            staff_context_data(request.user), 
            message, code
        )

    def post(self, request, pk=None) -> HttpResponse:
        action = request.POST.get("action")
        if action == "single":
            return self._handle_single_action(request, pk)
        
        role_ids = request.POST.getlist("role_ids")
        return self._handle_bulk_action(request, role_ids)




