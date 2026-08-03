from django import forms
from django_countries.fields import CountryField
from phonenumber_field.formfields import PhoneNumberField
from account.services.generic_service import valid_name, NAME_ERROR, INVALID_EMAIL
from directors.models import Director
from core.models import Title
from .models import (
    MembershipApplication,
    AssociatedHungarianCompany,
    Category,
    MemberRepresentative,
)


class ProfileForm(forms.Form):
    title = forms.ModelChoiceField(queryset=Title.objects.all())
    nationality = CountryField().formfield(required=True)
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(required=False)
    phone_number = PhoneNumberField(required=False)

class GeneralApplicationForm(forms.Form):
    proposer = forms.ModelChoiceField(queryset=Director.objects.all())
    other_business_interests = forms.CharField(
        required=False, widget=forms.Textarea)
    interest_in_hungary = forms.CharField(
        required=False, widget=forms.Textarea)
    main_challenges = forms.CharField(
        required=False, widget=forms.Textarea
    )
    areas_chamber_can_assist = forms.CharField(
        required=False, widget=forms.Textarea
    )
    declaration_accepted = forms.BooleanField(required=True)

class IndividualApplicationForm(forms.Form):
    registered_business_name = forms.CharField(
        max_length=255, required=False,
    )
    office_telephone = PhoneNumberField(required=False)
    type_of_business = forms.CharField(max_length=255, required=False)

class CorporateApplicationForm(forms.Form):
    company_name = forms.CharField(max_length=255, required=False)
    company_telephone = PhoneNumberField(required=False)
    company_email = forms.EmailField(required=False)
    company_address = forms.CharField(required=False, widget=forms.Textarea)
    core_business = forms.CharField(required=False, widget=forms.Textarea)
    business_type = forms.CharField(max_length=255, required=False)
    holding_company = forms.CharField(max_length=255, required=False)
    registration_number = forms.CharField(max_length=100, required=False)
    position = forms.CharField(max_length=150, required=False)
    number_of_employees = forms.IntegerField(min_value=0, required=False)
    year_established = forms.IntegerField(min_value=0, required=False)
    website = forms.URLField(required=False)

class MembershipApplicationForm(forms.Form):
    associated_hungarian_company = forms.ModelChoiceField(
        queryset=AssociatedHungarianCompany.objects.all(),
        required=False,
    )

class MemberRepresentativeForm(forms.Form):
    representative_type = forms.ChoiceField(
        choices=(MemberRepresentative.RepresentativeType.choices
        )
    )
    position = forms.CharField(max_length=255)

class AssociatedHungarianCompanyForm(forms.Form):
    company_name = forms.CharField(max_length=255)
    address = forms.CharField(required=False, widget=forms.Textarea)

class GeneralBenefitForm(forms.Form):
    description = forms.CharField(required=False, widget=forms.Textarea)

class BenefitForm(forms.Form):
    category = forms.ChoiceField(choices=(Category.Type.choices))
    description = forms.CharField(required=False, widget=forms.Textarea)
