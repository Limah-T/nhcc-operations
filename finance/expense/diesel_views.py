from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from account.services.profile_service import getUserName
from dashboard.views import diesel_temp_name
from nhcc_operations.services.generic_service import (
    intId, emptyFields, custom_form_errors
)
from .services.diesel_service import (
    dieselQueryset, totalMonthlyDiesel,
    dieselRetrieval, dieselFormValidator,
    prepareCreate, create, update, delete, 
)
from .forms import DieselForm

diesel_url_name = "diesel"

@method_decorator(login_required, "dispatch")
class DieselView(View):

    def get(self, request):
        queryset = dieselQueryset()
        total = totalMonthlyDiesel(queryset)
        return render(
            request,
            diesel_temp_name,
            {
                "diesel_records": queryset,
                "count": queryset.count(),
                "monthly_total_display": f"₦{total:,.2f}",
                "user_name":request.user.first_name[0]+request.user.last_name[0]
                
            },
        )

    def post(self, request):
        user_name = getUserName(request)
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
            else: value, message = "Create Error", error["error"]
        else: value, message = response.fields, response.errors
        queryset = dieselQueryset()
        errors = custom_form_errors(
            queryset, DieselForm(), value=value, message=message
        )
        return render(
            request, diesel_temp_name, context=errors, status=400
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
                supplier_name, litres, price, transport)
            if form.is_valid():
                error = update(
                    supplier_name, litres, price, tfare,
                    diesel, request.user, getUserName(request)
                )
                if error is None: return redirect(diesel_url_name)
                else: value, message, code = "Update Error", error["error"], 500
            else: value, message, code = form.non_field_errors, form.errors, 400
        else: value, message, code = "Empty Fields", ["All fields are empty"], 400
    else: value, message, code = "Diesel record", ["Diesel record not found."], 404
     
    queryset = dieselQueryset()
    errors = custom_form_errors(
        queryset, DieselForm(), value=value, message=message
    )
    return render(
        request, diesel_temp_name, context=errors, status=code
    )


@login_required
def delete_diesel(request, pk):
    if request.method != "POST":
        return redirect(diesel_url_name)
    if intId(pk):
        diesel = dieselRetrieval(pk)
        if diesel: 
            diesel.delete()
            return redirect(diesel_url_name)
    queryset = dieselQueryset()
    errors = custom_form_errors(
        queryset, DieselForm(), 
        value="Delete Error",
        message=["Diesel record not found."]
    )
    return render(
        request, diesel_temp_name, 
        context=errors, status=400
    )


@login_required
def delete_diesels(request):
    if request.method != "POST":
        return redirect(diesel_url_name)

    diesel_ids = request.POST.getlist("diesel_ids")
    if diesel_ids:
        error = delete(diesel_ids)
        if error is None:
            return redirect(diesel_url_name)
        else: message, code = error["error"], 500
    else: message, code = ["Diesel record not found"], 404
    queryset = dieselQueryset()
    errors = custom_form_errors(
        queryset=queryset, 
        form=DieselForm(), 
        value="Delete Error",
        message=message
    )
    return render(
        request, diesel_temp_name, 
        context=errors, status=code
    )
