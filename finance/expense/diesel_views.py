from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from decimal import Decimal
from .forms import DieselForm
from .models import Diesel
from dashboard.views import diesel_temp_name

@method_decorator(login_required, "dispatch")
class DieselView(View):

    def get(self, request):
        queryset = Diesel.objects.all().order_by('-created_at')

        now = timezone.now()
        monthly_total = sum(
            item.total for item in queryset if (
                item.created_at.month and item.created_at.year
            ) == (now.month and now.year)
            )
        return render(
            request,
            diesel_temp_name,
            {
                "diesel_records": queryset,
                "count": queryset.count(),
                "monthly_total_display": f"₦{monthly_total:,.2f}",
            },
        )

    def post(self, request):
        user_name = f"{request.user.first_name} {request.user.last_name}".strip()
        supplier_names = request.POST.getlist("supplier_name", [])
        litres = request.POST.getlist("litres", [])
        prices = request.POST.getlist("price", [])
        transports = request.POST.getlist("transport", [])
        diesel_list, errors = [], []
        for supplier, litre, price, transport in zip(
            supplier_names, litres, prices, transports):
            form = DieselForm(data={
                "litres":litre,
                "price":price,
                "supplier_name": supplier,
                "transport":transport
            })
            if form.is_valid():
                cleaned_litre = form.cleaned_data["litres"]
                cleaned_price = form.cleaned_data["price"]
                cleaned_supplier = form.cleaned_data["supplier_name"]
                fare = form.cleaned_data.get("transport")
                transport = fare if fare else Decimal("0.00")
                diesel_list.append(
                    Diesel(
                        litres=cleaned_litre, 
                        price=cleaned_price,
                        amount=cleaned_price*cleaned_litre, 
                        total=(cleaned_price*cleaned_litre)+transport,
                        supplier_name=cleaned_supplier.title(),
                        created_by_user=request.user,
                        month=timezone.now().strftime('%B'),
                        transport=transport,
                        created_by=user_name
                    )
                )
            else: errors.append(
                {
                    "value":"",
                    "errors": {"name": [form.errors]}
                }
            )
     
        if not errors:
            Diesel.objects.bulk_create(diesel_list)
            return redirect("diesel")
        return render(
            request, diesel_temp_name,
            {"form":DieselForm(), "diesel_errors":errors}
        )

@login_required
def edit_diesel(request, pk):
    if request.method != "POST":
        return redirect("diesel")

    diesel = Diesel.objects.filter(id=pk).first()
    errors = {}
    if diesel is None:
        queryset = Diesel.objects.all().order_by('-created_at')
        errors.update({
            "diesel_records": queryset, "count": queryset.count(),
                "diesel_errors":[
                {"value": "Diesel record", 
                    "errors": {
                        "supplier_name": ["Diesel record not found."]}
                }]})
        return render(request, diesel_temp_name, errors, status=400)

    supplier_name = request.POST.get("supplier_name", None)
    litres = request.POST.get("litres", None)
    price = request.POST.get("price", None)
    transport = request.POST.get("transport", None)
    tfare = transport.replace(",", "") if transport else None
    if all(x is None for x in [supplier_name, litres, price, tfare]):
        queryset = Diesel.objects.all().order_by('-created_at')
        errors.update({
            "diesel_records": queryset, "count": queryset.count(),
            "diesel_errors":[
                { "value": "", 
                "errors": {"supplier_name": ["Please complete all fields."]}
                }]})
        return render(request, diesel_temp_name, errors, status=400)
    form = DieselForm(
        data={
           "litres":litres,
            "price":price,
            "supplier_name": supplier_name,
            "transport":tfare        
        }
    )
    if not form.is_valid():
        queryset = Diesel.objects.all().order_by('-created_at')
        errors.update({
            "diesel_records": queryset, "count": queryset.count(),
            "diesel_errors":[
                { "value": form.non_field_errors, 
                "errors": {"name": form.errors}
                }]})
        return render(request, diesel_temp_name, errors, status=400)
   
    price = form.cleaned_data.get("price", diesel.price)
    litres = form.cleaned_data.get("litres", diesel.litres) 
    tfare = form.cleaned_data.get('transport', diesel.transport)
    diesel.supplier_name = form.cleaned_data.get(
        "supplier_name", diesel.supplier_name).title()
    diesel.litres, diesel.price = litres, price
    diesel.amount, diesel.total = price * litres, (price*litres)+tfare
    diesel.updated_by_user, diesel.transport = request.user, tfare
    diesel.updated_by = f"{request.user.first_name} {request.user.last_name}".strip()
    diesel.save()

    return redirect("diesel")


@login_required
def delete_diesel(request, pk):
    if request.method != "POST":
        return redirect("diesel")
    if pk is not None:
        diesel = Diesel.objects.filter(id=pk).first()
        if diesel:
            diesel.delete()
            return redirect("diesel")

    queryset = Diesel.objects.all().order_by('-created_at')
    return render(
        request,
        diesel_temp_name,
        {
            "diesel_records": queryset, 
            "count": queryset.count(), 
            "diesel_errors": [
                {"value": "Diesel record", 
                "errors": {"supplier_name": ["Diesel record not found."]}
            }]
        }, status=400,
    )


@login_required
def delete_diesels(request):
    if request.method != "POST":
        return redirect("diesel")

    diesel_ids = request.POST.getlist("diesel_ids")
    if diesel_ids:
        Diesel.objects.filter(id__in=diesel_ids).delete()
    return redirect("diesel")
