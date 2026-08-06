from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from dotenv import load_dotenv
from django.views import View
from account.services.profile_service import getNameAvatar
from dashboard.views import report_temp_name
from core.utils.pdf_generator import (
    pdf_generator, file_monthly_naming_constructor, file_yearly_naming_constructor
)
from .forms import ReportForm
from .services.report_service import (
    get_template_context, build_image_url, url_name
)
import os

load_dotenv()


def error_response(request, code):
    return render(
        request,
        template_name=report_temp_name,
        context={"user_name":getNameAvatar(request.user)},
        status=code
    )


@login_required
def reportOverview(request): 
    from datetime import date
    context = {"user_name":getNameAvatar(request.user)}
    context["years"] = range(2023, date.today().year + 1)    
    return render(
        request, template_name=report_temp_name,
        context=context, status=200
    )

@method_decorator(login_required, "dispatch")
class ReportManagementView(View):
    def get(self, request):
        return redirect(url_name)
    
    def _handle_report(self, request):
        report_type = request.POST.get("report_type")
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        form = ReportForm(data={
            "report_type":report_type, 
            "start_date":start, "end_date":end
        })
        if form.is_valid():
            report_type = form.cleaned_data["report_type"]
            if report_type != "yearly":     
                start = form.cleaned_data["start_date"]
                end = form.cleaned_data["end_date"]
                month, year = start.strftime("%B"), start.strftime("%Y")
                file_name = file_monthly_naming_constructor(
                    report_type, month, year, start, end)
            else:
                year = int(request.GET.get("year"))
                month = None
                file_name = file_yearly_naming_constructor(report_type, year)
            details = get_template_context(
                report_type, request.user, start, end, month, year)   
            context = details["context"]
            context.update({
                "logo_url": build_image_url(),
                "company_email": os.environ.get("company_email")
            })
            html_string = render_to_string(
                template_name=details["template"],
                context=context, request=request
            )
            css_path = "css/report/report.css"
            response = pdf_generator(html_string, request, file_name, css_path)
            return response
        
        return error_response(request, code=400)

    def post(self, request) -> HttpResponse:

        return self._handle_report(request)
    




