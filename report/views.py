from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect
from account.services.profile_service import getFullName
from finance.expense.services.expense_service import (
    expenseQueryset, totalMonthlyExpenses, 
    totalExpenseRecords,
)
from django.http import HttpResponse
from dashboard.views import report_temp_name
from .forms import DateForm
from .services.report_service import (
    futureDate, setDate, pdfGenerator
)

url_name = "reports"
expense_report_temp = "report/expenses.html"

def report_context_data(request, start_date, end_date)-> dict:
    queryset = expenseQueryset()
    total_expenses = totalMonthlyExpenses(queryset)
    total_records = totalExpenseRecords(start_date, end_date)
    generated_by = getFullName(request)
    generated_at = timezone.now()
 
    return {
        "expenses":queryset,
        "total_expenses":total_expenses,
        "total_records":total_records,
        "generated_by":generated_by,
        "generated_at":generated_at,
        "report_period": f"{start_date:%d %b %Y} - {end_date:%d %b %Y}",   
    }


@login_required
def report_view(request):
    return render(
        request,
        report_temp_name,

        status=200
    )


@login_required
def generate_report(request):
    if request.method != "POST":
        return redirect(url_name)
    
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    if not start_date or not end_date:
        start_date, end_date = setDate()

    form = DateForm(data={"start_date":start_date, "end_date":end_date})
    if form.is_valid():
        if not futureDate(
            form.cleaned_data["start_date"], 
            form.cleaned_data["end_date"]
        ):
            html_string = render_to_string(
                expense_report_temp,
                report_context_data(request, start_date, end_date),
                request=request,
            )
            pdf = pdfGenerator(html_string, request)
            response = HttpResponse(pdf, content_type="application/pdf")
            response["Content-Disposition"] = 'inline; filename="expense_report.pdf"'

            return response
        else:
            message = {"Date": ["Report Date is in the future."]}
    else: message = form.errors
    return render(
        request, report_temp_name,
        context={"errors":message},
        status=400
    )


now = timezone.now()
month = now.strftime("%B")
year = now.year
expense_report_temp = "report/expenses.html"




