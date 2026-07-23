from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dashboard.views import staff_account_temp_name
from .services.staff_service import (
    url_name, staffContextData, staffFormValidator,
    staffRetrieval, create, update
)
from account.services.profile_service import getFullName
from nhcc_operations.services.generic_service import (
    emptyFields, intId, staff_404, empty_fields_error
)
from decimal import Decimal
from .forms import StaffFormset, StaffForm

@login_required
def staffView(request):
    if request.method != "POST":
        return redirect(url_name)
    roles = request.POST.getlist("roles", [])
    full_names = request.POST.getlist("full_names", [])
    emails = request.POST.getlist("emails", [])
    phone_numbers = request.POST.getlist("phone_numbers", [])
    salaries = request.POST.getlist("salaries", [])
    account_numbers = request.POST.getlist("account_numbers", [])
    bank_names = request.POST.getlist("bank_names", [])
    bank_full_names = request.POST.getlist("bank_full_names", [])
    employment_dates = request.POST.getlist("employment_dates", [])

    formset = StaffFormset()
    if not emptyFields([
        roles, full_names, emails, phone_numbers, 
        salaries, account_numbers, bank_names, 
        bank_full_names]
    ):
        data = {
            "roles":roles, "full_names":full_names,
            "emails":emails, "phone_numbers":phone_numbers,
            "salaries":salaries, "bank_names":bank_names,
            "bank_full_names":bank_full_names,
            "account_numbers":account_numbers,
            "employment_dates":employment_dates
        }
        response = staffFormValidator(data)
        if not isinstance(response, StaffForm):
            error = create(
                response, {"user":request.user, "user_name":getFullName(request)}
            )
            if error is None:
                messages.success(request, "Staff added successfully.")
                return redirect(url_name)
            else: message, code = error["error"], error["status"]
        else: message, code = response.errors, 400
    else: message, code = empty_fields_error, 400
    messages.error(request, message)
    return render(
        request, staff_account_temp_name,
        staffContextData(formset), status=code
    )

@login_required
def editStaffView(request, pk):
    if request.method != "POST":
        return redirect(url_name)
    if intId(pk):
        staff = staffRetrieval(pk)
        if staff:
            role = request.POST.get("role")
            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            phone_number = request.POST.get("phone_number")
            salary = request.POST.get("amount")
            account_numbers = request.POST.get("account_numbers")
            bank_name = request.POST.get("bank_name")
            bank_full_name = request.POST.get("account_name")
            employment_date = request.POST.get("employment_date")
            formset = StaffFormset()
   
            if not emptyFields([
                role, full_name, email, phone_number, 
                salary, account_numbers, bank_name, 
                bank_full_name]
            ):
                amount = Decimal(salary.replace(",", ""))
                data = {
                    "role":role, "full_name":full_name,
                    "email":email, "phone_number":phone_number,
                    "salary":amount, 
                    "bank_name":bank_name,
                    "bank_full_name":bank_full_name,
                    "account_number":account_numbers,
                    "employment_date":employment_date
                }
     
                form = StaffForm(data=data)
                if form.is_valid():
                    error = update(
                        staff, form.cleaned_data, {"user":request.user, "user_name":getFullName(request)}
                    )
                    if error is None:
                        messages.success(request, "Staff record updated successfully.")
                        return redirect(url_name)
                    else: message, code = error["error"], error["status"]
                else: message, code = form.errors, 400
            else: message, code = empty_fields_error, 400
        else: message, code = staff_404["error"], staff_404["status"]
    else: message, code = staff_404["error"], staff_404["status"]
    messages.error(request, message)
    return render(
        request, staff_account_temp_name,
        staffContextData(formset), status=code
    )