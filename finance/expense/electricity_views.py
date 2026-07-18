from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from dashboard.views import electricity_temp_name
from nhcc_operations.services.generic_service import ekedc_404
from account.services.profile_service import getFullName
from nhcc_operations.services.generic_service import intId
from .services.electricity_service import (
    ekedcQuerySet, ekedcRetrieval, ekedcFormValidator,
    totalMonthlyPrepaid,
    prepareCreate, create, update,
    delete_one, delete_many
)
from .forms import ElectricityForm

url_name = "electricity"

def ekedc_home_context(request, error_message) -> dict:
    queryset = ekedcQuerySet()
    total = totalMonthlyPrepaid(queryset)
    return {
        "electricity_records": queryset,
        "count": queryset.count(),
        "monthly_total_display": f"₦{total:,.2f}",
        "errors": error_message,
        "user_name":getFullName(request)
    }

@method_decorator(login_required, name="dispatch")
class ElectricityView(View):
    def get(self, request):  
        return render(
            request,
            electricity_temp_name,
            ekedc_home_context(request, error_message=None),
            status=200
        )

    def post(self, request):
        kwhs = request.POST.getlist("kwh", [])
        amounts = request.POST.getlist("amount", [])
        if all(x is None for x in [kwhs, amounts]):
            message = {"Empty Fields": ["Please complete all fields."]}
            return render(
            request, electricity_temp_name,
            ekedc_home_context(request, error_message=message)
        )

        response = prepareCreate(
            kwhs, amounts, request.user.id, getFullName(request)
            )
        if not isinstance(response, ElectricityForm):
            error = create(response)
            if error is None:
                return redirect(url_name)
            else: message, code = {"Create Error": error["error"]}, error["status"]
        else: message, code = response.errors, 400

        return render(
            request, electricity_temp_name,
            ekedc_home_context(request, error_message=message),
            status=code
        )


@login_required
def edit_electricity(request, pk):
    if request.method != "POST":
        return redirect(url_name)
    
    if intId(pk):
        ekedc = ekedcRetrieval(pk)
        if ekedc:             
            kwh = request.POST.get("kwh")
            amount = request.POST.get("amount").replace(",", "") 
            form = ekedcFormValidator(kwh, amount)
            if form.is_valid():
                error = update(
                    ekedc, kwh, amount, request.user.id, 
                    getFullName(request)
                )
                if error is None:
                    return redirect(url_name)
                else: message, code = {"Update Error": error["error"]}, error["status"]
            else: message, code = form.errors, 400
        else: message, code = {"Not Found": ekedc_404["error"]}, ekedc_404["status"]
    else: message, code = {"Not Found": ekedc_404["error"]}, ekedc_404["status"]
    return render(
        request, electricity_temp_name,
        ekedc_home_context(request, error_message=message),
        status=code
    )

@login_required
def delete_electricity(request, pk):
    if request.method != "POST":
        return redirect(url_name)
    if intId(pk):
        ekedc = ekedcRetrieval(pk)
        if ekedc:
            error = delete_one(ekedc)
            if error is None:
                return redirect(url_name)
            else: 
                message, code = {"Delete Error": error["error"]}, error["status"]
        else: 
            message, code = {"Not Found": ekedc_404["error"]}, ekedc_404["status"]
    else: 
        message, code = {"Not Found": ekedc_404["error"]}, ekedc_404["status"]
    return render(
        request, electricity_temp_name,
        ekedc_home_context(request, error_message=message),
        status=code
    )
    

@login_required
def delete_electricities(request):
    if request.method != "POST":
        return redirect(url_name)

    ekedc_ids = request.POST.getlist("electricity_ids")
    if ekedc_ids:
        error = delete_many(ekedc_ids)
        if error is None:
            return redirect(url_name)
        else:
            message, code = {"Delete Error", error["error"]}, error["status"]
    else:
        message, code = {"Not Found", ekedc_404["error"]}, ekedc_404["status"]

    return render(
        request, electricity_temp_name,
        ekedc_home_context(request, error_message=message),
        status=code
    )
