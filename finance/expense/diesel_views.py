from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from account.services.profile_service import getFullName
from nhcc_operations.services.generic_service import diesel_404
from dashboard.views import diesel_temp_name
from nhcc_operations.services.generic_service import (
    intId, emptyFields
)
from .services.diesel_service import (
    dieselQueryset, totalMonthlyDiesel,
    dieselRetrieval, dieselFormValidator,
    prepareCreate, create, update, 
    delete_one, delete_many
)
from .forms import DieselForm

diesel_url_name = "diesel"

def diesel_home_context(request, error_message)->dict:
    queryset = dieselQueryset()
    total = totalMonthlyDiesel(queryset)
    return {
                "diesel_records": queryset,
                "count": queryset.count(),
                "monthly_total_display": f"₦{total:,.2f}",
                "errors": error_message,
                "user_name":request.user.first_name[0]+request.user.last_name[0],
                    
            }

@method_decorator(login_required, "dispatch")
class DieselView(View):

    def get(self, request):
        return render(
            request, diesel_temp_name,
            diesel_home_context(request, error_message=None),
            status=200
        )

    def post(self, request):
        user_name = getFullName(request)
        supplier_names = request.POST.getlist("supplier_name", [])
        litres = request.POST.getlist("litres", [])
        prices = request.POST.getlist("price", [])
        transports = request.POST.getlist("transport", [])
        response = prepareCreate(
            supplier_names, litres, prices,
            transports, user_name, request.user.id
        )
        if not isinstance(response, DieselForm):
            error = create(response)
            if error is None:
                return redirect(diesel_url_name)
            else: 
                message, code = {"Create Error": error["error"]}, error["status"]
        else: 
            message, code = response.errors, 400
        return render(
            request, diesel_temp_name,
            diesel_home_context(request, error_message=message),
            status=code
        )
     
        
@login_required
def edit_diesel(request, pk):
    if request.method != "POST": return redirect(diesel_url_name)
    if not intId(pk): return redirect(diesel_url_name)
    
    diesel = dieselRetrieval(pk)
    if diesel:        
        supplier_name = request.POST.get("supplier_name", None)
        litres = request.POST.get("litres", None)
        price = request.POST.get("price", None)
        transport = request.POST.get("transport", None)
        tfare = transport.replace(",", "") if transport else None
        if not emptyFields([supplier_name, litres, price, tfare]):
            form = dieselFormValidator(
                supplier_name, litres, price, tfare)
            if form.is_valid():
                error = update(
                    form, diesel, request.user, getFullName(request)
                ) 
                if error is None: 
                    return redirect(diesel_url_name)
                else: message, code = {"Update Error": error["error"]}, error["status"]
            else: message, code = form.errors, 400
        else: message, code = {"Not Found": diesel_404["error"]}, diesel_404["status"]
    else: message, code = {"Not Found": diesel_404["error"]}, diesel_404["status"]
    return render(
        request, diesel_temp_name,
        diesel_home_context(request, error_message=message),
        status=code
    )
    

@login_required
def delete_diesel(request, pk):
    if request.method != "POST":
        return redirect(diesel_url_name)
    if intId(pk):
        diesel = dieselRetrieval(pk)
        if diesel: 
            error = delete_one(diesel)
            if error is None:
                return redirect(diesel_url_name)
            else:
                message, code = {"Delete Error": error["error"]}, error["status"]
        else: 
            message, code = {"Not Found": diesel_404["error"]}, diesel_404["status"]
    else: 
        message, code = {"Not Found": diesel_404["error"]}, diesel_404["status"]
    return render(
        request, diesel_temp_name,
        diesel_home_context(request, error_message=message),
        status=code
    )


@login_required
def delete_diesels(request):
    if request.method != "POST":
        return redirect(diesel_url_name)

    diesel_ids = request.POST.getlist("diesel_ids")
    if diesel_ids:
        error = delete_many(diesel_ids)
        if error is None:
            return redirect(diesel_url_name)
        else:
            message, code = {"Delete Error": error["error"]}, error["status"]
    else: 
        message, code = {"Not Found": diesel_404["error"]}, diesel_404["status"]
    return render(
        request, diesel_temp_name,
        diesel_home_context(request, error_message=message),
        status=code
    )
