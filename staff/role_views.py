from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dashboard.views import staff_account_temp_name
from .services.role_service import (
    roleRetrieval, 
    roleFormValidator, create, update,
    delete_one, delete_many
)
from .services.staff_service import url_name, staffContextData
from account.services.profile_service import getFullName
from nhcc_operations.services.generic_service import (
    emptyFields, intId, role_404, empty_fields_error
)
from .forms import RoleForm, RoleFormset


@login_required
def staffRecords(request):
    return render(
        request, 
        staff_account_temp_name, 
        staffContextData(),
        status=200
    )

@login_required
def roleView(request):
    if request.method != "POST":
        return redirect(url_name)
    roles = request.POST.getlist("names", [])
    formset = RoleFormset()
    if not emptyFields(roles):
        response = roleFormValidator(roles)
        if not isinstance(response, RoleForm):
            data = {
                "user": request.user, 
                "user_name":getFullName(request)
            }
            error = create(data, response)
            if error is None:
                messages.success(request, "Role added successfully.")
                return render(
                    request, staff_account_temp_name,
                    context=staffContextData(formset), status=200
                )
            message, code = error["error"], error["status"]
        else: message, code = response.errors, 400 
    else: message, code = empty_fields_error, 400
    messages.error(request, message)
    return render(
        request, staff_account_temp_name,
        context=staffContextData(formset), status=code
    )
            

@login_required     
def editRoleView(request, pk):
    if request.method != "POST":
        return redirect(url_name)
    role_name = request.POST.get("role_name", "")
    if intId(pk):
        form = RoleForm(data={"name":role_name})
        formset = RoleFormset()
        if form.is_valid():
            role = roleRetrieval(pk)
            if role:
                data = {"name": form.cleaned_data["name"]}
                error = update(role, data)
                if error is None:
                    messages.success(request, "Role updated successfully.")
                    return render(
                        request, staff_account_temp_name,
                        context=staffContextData(formset), status=200
                    )
                else: message, code = error["error"], error["status"]
            else: message, code = role_404["error"], role_404["status"]
        else: message, code = form.errors, 400
    else: message, code = role_404["error"], role_404["status"]
    messages.error(request, message)
    return render(
        request, staff_account_temp_name,
        context=staffContextData(formset), status=code
    )

@login_required
def deleteRole(request, pk):
    if request.method != "POST":
        return redirect(url_name)
    if intId(pk):
        role = roleRetrieval(pk)
        if role:
            error = delete_one(role)
            if error is None:
                messages.success(request, "Role deleted successfully")
                return redirect(url_name)
            message, code = error["error"], error["status"]
        else: message, code = role_404["error"], role_404["status"]
    else: message, code = role_404["error"], role_404["status"]
    messages.error(request, message)
    return render(
        request, staff_account_temp_name,
        context=staffContextData(None), status=code
    )

@login_required
def deleteRoles(request):
    if request.method != "POST":
        return redirect(url_name)
    role_ids = request.POST.getlist("role_ids", [])

    error = delete_many(role_ids)
    if error is None:
        messages.success(request, "Roles deleted successfully")
        return redirect(url_name)
    message, code = error["error"], error["status"]
    messages.error(request, message)
    return render(
        request, staff_account_temp_name,
        context=staffContextData(None), status=code
    )



