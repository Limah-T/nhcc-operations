from django.shortcuts import render
from django.views import View
from django.template.loader import render_to_string
from report.services.report_service import pdf_generator

membership_application_temp = "members/application_form.html"
class MembershipApplicationTemplateView(View):

    def get(self, request):

        html_string = render_to_string(
            template_name=membership_application_temp,
            request=request,
        )

        return pdf_generator(
            html_string=html_string,
            request=request,
            file_name="membership_application_form.pdf",
            # css_path="css/members/application_form.css"
        )
        