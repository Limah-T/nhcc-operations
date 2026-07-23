from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.shortcuts import render
from django.shortcuts import redirect
from account.services.profile_service import getNameAvatar
from dashboard.views import report_temp_name
from .forms import DateForm
from .services.report_service import (
    futureDate, setDate, setMonthYear, 
    pdfGenerator, getTemplateContext,
    fileNamingConstructor, url_name
)

@login_required
def report_view(request):  
    return render(
        request,
        template_name=report_temp_name,
        context={"user_name":getNameAvatar(request)},
        status=200
    )

@login_required
def generate_report(request):
    if request.method != "POST":
        return redirect(url_name)
    report_type = request.POST.get("report_type")
    start = request.POST.get("start_date")
    end = request.POST.get("end_date")

    if not start or not end: start, end = setDate()

    form = DateForm(data={
        "report_type":report_type, 
        "start_date":start, "end_date":end
    })
    if form.is_valid():
        report_type = form.cleaned_data["report_type"]
        start = form.cleaned_data["start_date"]
        end = form.cleaned_data["end_date"]
        if futureDate(start, end):
            message = {"Date": ["Report Date is in the future."]}
        else:
            month, year = setMonthYear()
            file_name = fileNamingConstructor(report_type, month, year, start, end)
            details = getTemplateContext(
                report_type, request, start, end, month, year)
            html_string = render_to_string(
                template_name=details["template"],
                context=details["context"], request=request
            )
            response = pdfGenerator(html_string, request, file_name)
            return response
    else: message = form.errors
    return render(
        request, report_temp_name, context={"errors":message}, status=400
    )




