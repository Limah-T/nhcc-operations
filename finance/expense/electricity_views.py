from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from .forms import ElectricityForm
from .models import EKEDC
from dashboard.views import electricity_temp_name


@method_decorator(login_required, name="dispatch")
class ElectricityView(View):
    def get(self, request):
        queryset = EKEDC.objects.all().order_by('-created_at')
        now = timezone.now()
        monthly_total = sum(
            item.amount for item in queryset 
                if (item.created_at.year and item.created_at.month
                    ) == (now.year and now.month
                )
        )
        return render(
            request,
            electricity_temp_name,
            {
                "electricity_records": queryset,
                "count": queryset.count(),
                "monthly_total_display": f"₦{monthly_total:,.2f}",
                "user_name":request.user.first_name[0]+request.user.last_name[0]
            },
        )

    def post(self, request):
        user_name = f"{request.user.first_name} {request.user.last_name}".strip()
        kwhs = request.POST.getlist("kwh", [])
        amounts = request.POST.getlist("amount", [])
        errors = {}
        if all(x is None for x in [kwhs, amounts]):
            queryset = EKEDC.objects.all().order_by('-created_at')
            return render(
                request,
                electricity_temp_name,
                errors.update({
                    "electricity_records": queryset,
                    "count": queryset.count(),
                    "electricity_errors": [
                        {
                            "value": "Entry", 
                            "errors": {"name": ["Please complete all fields."]}}
                        ],
                }),
            )
        electricity_list, errors = [], []
        for kwh, amount in zip(kwhs, amounts):
            form = ElectricityForm(
                data={
                    "kwh":kwh,
                    "amount":amount.replace(",", "")
                }
            )
            if not form.is_valid():
                queryset = EKEDC.objects.all().order_by('-created_at')
                return render(
                request,
                electricity_temp_name,
                errors.update({
                    "electricity_records": queryset,
                    "count": queryset.count(),
                    "electricity_errors": [
                        {
                            "value": form.fields, 
                            "errors": {"name": form.errors}}
                        ],
                }))
            electricity_list.append(
                EKEDC(
                    kwh=kwh,
                    amount=amount,
                    month=timezone.now().strftime("%B"),
                    created_by_user=request.user,
                    created_by=user_name,
                    updated_by=user_name,
                )
            )
        EKEDC.objects.bulk_create(electricity_list)
        return redirect("electricity")


@login_required
def edit_electricity(request, pk):
    if request.method != "POST":
        return redirect("electricity")
    electricity = EKEDC.objects.filter(id=pk).first()
    if electricity is None:
        queryset = EKEDC.objects.all().order_by('-created_at')
        return render(
            request,
            electricity_temp_name,
            {
                "electricity_records": queryset, 
                "count": queryset.count(), 
                "electricity_errors": [
                    {
                        "value": "Electricity record", 
                        "errors": {"name": ["Electricity record not found."]}
                    }
                ]}, status=400,
        )
    kwh = request.POST.get("kwh", electricity.kwh)
    amount = request.POST.get("amount", electricity.amount).replace(",", "")
    form = ElectricityForm(data={"kwh":kwh, "amount":amount})
    if not form.is_valid():
        queryset = EKEDC.objects.all().order_by('-created_at')
        return render(
            request,
            electricity_temp_name,
            {
                "electricity_records": queryset, 
                "count": queryset.count(), 
                "electricity_errors": [
                    {
                        "value": form.fields, 
                        "errors": {"name": form.errors}
                    }
                ]}, status=400,
        )
    if electricity.kwh != kwh or electricity.amount != amount:
        electricity.kwh = kwh
        electricity.amount = amount
        electricity.updated_by_user = request.user
        electricity.updated_by = \
            f"{request.user.first_name} {request.user.last_name}".strip()
        electricity.save()
    return redirect("electricity")


@login_required
def delete_electricity(request, pk):
    if request.method != "POST":
        return redirect("electricity")

    electricity = EKEDC.objects.filter(id=pk).first()
    if electricity:
        electricity.delete()
        return redirect("electricity")

    queryset = EKEDC.objects.all().order_by('-created_at')
    return render(
        request,
        electricity_temp_name,
        {
            "electricity_records": queryset, 
            "count": queryset.count(), 
            "electricity_errors": [
                {"value": "Electricity record",
                "errors": {"name": ["Electricity record not found."]}}]},
        status=404,
    )


@login_required
def delete_electricities(request):
    if request.method != "POST":
        return redirect("electricity")

    electricity_ids = request.POST.getlist("electricity_ids")
    if electricity_ids:
        EKEDC.objects.filter(id__in=electricity_ids).delete()
    return redirect("electricity")
