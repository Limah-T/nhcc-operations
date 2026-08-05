from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dashboard.views import staff_account_temp_name
from ..services.account_details_service import (
    bankAccountQueryset, bankAcctRetrieval, 
    bankAccountFormValidator, create
)
from ..services.staff_service import staffContextData
from account.services.profile_service import getFullName
from core.utils.generic_service import (
    emptyFields, intId, role_404, empty_fields_error
)
from ..services.staff_service import url_name
from ..forms import AccountDetailForm, AccountDetailFormset

@login_required
def bankAccountView(request):
    if request.method != "POST":
        return redirect(url_name)
    
    account_numbers = request.POST.getlist("", [])
    bank_names = request.POST.getlist("", [])
    bank_full_names = request.POST.getlist("", [])


    formset = AccountDetailFormset()
    if not emptyFields([account_numbers, bank_names, bank_full_names]):
        data = {
            "bank_full_names":bank_full_names,
            "bank_names":bank_names,
            "account_numbers":account_numbers
        }
        response = bankAccountFormValidator(data)
        if not isinstance(response, AccountDetailForm):
            error = create({
                "user":request.user, "user_name":getFullName(request)
            }, response)
            if error is None:
                messages.success(request, "Account(s) added successfully.")
                return redirect(url_name)
            message, code = error["error"], error["status"]
        else: message, code = response.errors, 400
    else: message, code = empty_fields_error, 400
    messages.error(request, message)
    return render(
        request, 
        staff_account_temp_name,
        staffContextData(formset),
        status=code
    )
