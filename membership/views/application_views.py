from django.shortcuts import render
from django.views import View
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.contrib import messages
from core.utils.pdf_generator import pdf_generator
from ..forms import (
    ProfileForm, GeneralApplicationForm, 
    CorporateApplicationForm, MemberRepresentativeForm,
    IndividualApplicationForm, MembershipApplicationForm,
    
)

membership_application_temp = "membership/dashboard.html"
member_list_temp = "members/member_list.html"

context = {
    "profile_form": ProfileForm(),
    "general_application_form": GeneralApplicationForm(),
    "corporate_application_form": CorporateApplicationForm(),
    "representative_form": MemberRepresentativeForm(),
    "individual_application_form": IndividualApplicationForm(),
    "membership_application_form": MembershipApplicationForm(),

}

membership_url = "membership_application"

@method_decorator(login_required, "dispatch")
class MembershipApplicationSubmission(View):

    def get(self, request):
        print("INSIDE THE VIEW")
        return render(
            request, membership_application_temp,
            context=context
            )

    def post(self, request):
        print("REQUEST", request)
        return redirect(membership_url)

@method_decorator(login_required, "dispatch")
class MembershipApplicationSubmission(View):

    def get(self, request):
        print("INSIDE THE VIEW")
        return render(
            request, membership_application_temp,
            context=context
            )

    def post(self, request):
        print("REQUEST", request)
        return redirect(membership_url)

@method_decorator(login_required, "dispatch")
class Members(View):

    def get(self, request):
        print("INSIDE THE VIEW")
        return render(
            request, member_list_temp,
            context=context
            )

    def post(self, request):
        print("REQUEST", request)
        return redirect(membership_url)

