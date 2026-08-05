from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http.response import HttpResponse
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.views import View
from django.contrib import messages
from dashboard.views import staff_account_temp_name
from core.utils.custom_exceptions import NothingToUpdateError
from core.utils.error_responses import (
    ROLE_404, ROLES_404, SERVER_ERROR, 
    ROLE_DELETE_PROTECTED, ROLES_DELETE_PROTECTED,
    ROLE_CONFLICT, ROLES_CONFLICT, NOTHING_TO_UPDATE,
)
from core.utils.success_responses import (
    ROLE_CREATED, ROLES_CREATED, ROLE_UPDATED, 
    ROLE_DELETED, ROLES_DELETED
)
from ..services.role_service import (
    RolePayloadParser, RoleDataInserter, 
    RoleDataUpdater, RoleDataDeleter
)
from ..services.staff_service import staff_context_data
from .staff_views import error_response, staff_url_name
from ..forms import RoleForm
from ..models import Role


@method_decorator(login_required, "dispatch")
class RoleGetCreatetView(View):

    def get(self, request):
        return render(
            request=request, 
            template_name=staff_account_temp_name,
            context=staff_context_data(request.user),
            status=200
        )

    def _single_handler(self, request):
        field_data = RolePayloadParser(request).parse_single()
        form = RoleForm(data=field_data)
        if form.is_valid():
            try:
                role = RoleDataInserter(form.cleaned_data, request.user)
                role.create_single()
                messages.success(request, ROLE_CREATED)
                return redirect(staff_url_name)
            except IntegrityError:
                code = 400
                messages.error(request, ROLE_CONFLICT)
            except Exception as error:
                code = 500
                messages.error(request, SERVER_ERROR)
        else: 
            code = 400
            messages.error(request, form.errors)
        return error_response(request, code)
    
    def _bulk_handler(self, request):
        field_data = RolePayloadParser(request).parse_bulk()
        role_list = []
        for name in field_data["name"]:
            form = RoleForm(data={"name":name})
            if not form.is_valid():
                messages.error(request, form.errors)
                return error_response(request, code=400)
            role_list.append(form.cleaned_data)

        try:
            role = RoleDataInserter(role_list, request.user)
            role.create_bulk()
            messages.success(request, ROLES_CREATED)
            return redirect(staff_url_name)
        except IntegrityError:
            code = 400
            messages.error(request, ROLES_CONFLICT)
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
class RoleUpdateView(View):
    def get(self, request, id=None):
        return redirect(staff_url_name)

    def _single_handler(self, request, id):
        field_data = RolePayloadParser(request).parse_single()
        form = RoleForm(data=field_data)
        if form.is_valid():
            try:
                role = RoleDataUpdater(form.cleaned_data, request.user)
                role.update_single(id)
                messages.success(request, ROLE_UPDATED)
                return redirect(staff_url_name)
            except Role.DoesNotExist:
                code = 404
                messages.error(request, ROLE_404)
            except NothingToUpdateError:
                code = 400
                messages.error(request, NOTHING_TO_UPDATE)
            except IntegrityError:
                code = 400
                messages.error(request, ROLE_CONFLICT)
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

        return redirect(staff_url_name)
    
class RoleDeleteView(View):
    def get(self, request, id=None):
       return redirect(staff_url_name)

    def _single_handler(self, request, id:int):
        try:
            RoleDataDeleter().delete_single(id)
            messages.success(request, ROLE_DELETED)
            return redirect(staff_url_name)
        except Role.DoesNotExist:
            code = 404
            messages.error(request, ROLE_404)
        except ProtectedError:
            code = 400
            messages.error(request, ROLE_DELETE_PROTECTED)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)
        return error_response(request, code)

    def _bulk_handler(self, request, role_ids:list):
        try:
            if role_ids:
                RoleDataDeleter().delete_bulk(role_ids)
                messages.success(request, ROLES_DELETED)
            return redirect(staff_url_name)
        except Role.DoesNotExist:
            code = 404
            messages.error(request, ROLES_404)
        except ProtectedError:
            code = 400
            messages.error(request, ROLES_DELETE_PROTECTED)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)
        return error_response(request, code)

    def post(self, request, id=None) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
            return self._single_handler(request, id)
        elif action == "bulk":
            role_ids = request.POST.getlist("role_ids")
            return self._bulk_handler(request, role_ids)

        return redirect(staff_url_name)
    