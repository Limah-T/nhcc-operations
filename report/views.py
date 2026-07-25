from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.http.response import HttpResponse
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect
from django.views import View
from account.services.profile_service import getNameAvatar
from dashboard.views import report_temp_name
from nhcc_operations.services.http_response_services import error_response
from .forms import ReportForm
from .services.report_service import (
    pdf_generator, get_template_context,
    file_naming_constructor, build_image_url, 
    url_name
)

@login_required
def reportOverview(request):  
    return render(
        request,
        template_name=report_temp_name,
        context={"user_name":getNameAvatar(request.user)},
        status=200
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
            start = form.cleaned_data["start_date"]
            end = form.cleaned_data["end_date"]
            now = timezone.now()
            month, year = now.strftime("%B"), now.strftime("%Y")
            file_name = file_naming_constructor(
                report_type, month, year, start, end)
            details = get_template_context(
                report_type, request.user, start, end, month, year)
            context = details["context"]
            context.update({"logo_url": build_image_url(request)})
            html_string = render_to_string(
                template_name=details["template"],
                context=context, request=request
            )
            response = pdf_generator(html_string, request, file_name)
            return response
        else: message = form.errors
        return error_response(request, report_temp_name, None, message, 400)

    def post(self, request) -> HttpResponse:

        return self._handle_report(request)
    




