from django.shortcuts import render
from django.views import View
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from nhcc_operations.services.http_response_services import (
    error_response, success_response
) 
from nhcc_operations.services.generic_service import category_404
from .forms import CategoryForm
from dashboard.views import category_temp_name
from account.services.profile_service import getNameAvatar
from .services.category_service import (
    CategoryPayloadParser, category_context_data,
    create_single, create_bulk, update_single,
    delete_single, delete_bulk
)

category_url_name = "category"

@login_required
def categoryOverview(request):
    return render(
        request=request, 
        template_name=category_temp_name,
        context={
            "user_name":getNameAvatar(request.user)
        }
    )   

@method_decorator(login_required, name="dispatch")
class CategoryManagementView(View):
    def get(self, request):
        return render(
            request=request, 
            template_name=category_temp_name, 
            context=category_context_data()
        )

    def _handle_single_action(self, request):
        """Orchestrates single workflow"""
        field_data = CategoryPayloadParser(request).parse_single()
        form = CategoryForm(data=field_data)
        if form.is_valid():
            error = create_single(form.cleaned_data, request.user)
            if error is None:
                message = "Category created successfully."
                return success_response(request, category_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = form.errors, 400
        return error_response(
            request, category_temp_name, 
            category_context_data(), message, code
        )
    
    def _handle_bulk_action(self, request):
        """Orchestrates bulk workflow"""
        field_data = CategoryPayloadParser(request).parse_bulk()
        category_list = []
        can_proceed = True
        for name in field_data["name"]:
            form = CategoryForm(data={"name":name})
            if not form.is_valid():
                message, code = form.errors, 400
                can_proceed = False
                break
            category_list.append(form.cleaned_data)

        if can_proceed:
            error = create_bulk(category_list, request.user)
            if error is None:
                message = "Category records created successfully."
                return success_response(request, category_url_name, message)
            else: 
                message, code = error[0], error[1]
        
        return error_response(
            request, category_temp_name, 
            category_context_data(), message, code
        )

    def post(self, request) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
            return self._handle_single_action(request)
        
        return self._handle_bulk_action(request)

@method_decorator(login_required, "dispatch")
class CategoryUpdateView(View):
    def get(self, request, pk=None):
        return success_response(request, category_url_name, None)

    def _handle_single_action(self, request, id):
        """Orchestrates a single workflow"""

        field_data = CategoryPayloadParser(request).parse_single()
        form = CategoryForm(data=field_data)
        if form.is_valid():
            error = update_single(id, form.cleaned_data, request.user)
            if error is None:
                message = "Category updated successfully."
                return success_response(request, category_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = form.errors, 400
        return error_response(
            request, category_temp_name, 
            category_context_data(), message, code
        )

    def post(self, request, pk=None):
        action = request.POST.get("action")
        if action == "single":
           
           return self._handle_single_action(request, pk)

        return success_response(request, category_url_name, None)

@method_decorator(login_required, "dispatch")
class CategoryDeleteView(View):
    def get(self, request):
       return success_response(request, category_url_name, None)

    def _handle_single_action(self, request, pk:int):
        """Orchestrates a single workflow"""
        
        error = delete_single(pk)
        if error is None:
            message = "Category deleted successfully."
            return success_response(request, category_url_name, message)
        
        message, code = error[0], error[1]
        return error_response(
            request, category_temp_name, 
            category_context_data(), message, code
        )

    def _handle_bulk_action(self, request, category_ids:list):
        """Orchestrates bulk workflow"""

        if category_ids:
            error = delete_bulk(category_ids)
            if error is None:
                message = "Category deleted successfully"
                return success_response(request, category_url_name, message)
            
            message, code = error[0], error[1]
        else: message, code = category_404, 400
        return error_response(
            request, category_temp_name, 
            category_context_data(), message, code
        )

    def post(self, request, pk=None) -> HttpResponse:
        action = request.POST.get("action")
        if action == "single":
            return self._handle_single_action(request, pk)
        
        category_ids = request.POST.getlist("category_ids")
        return self._handle_bulk_action(request, category_ids)
