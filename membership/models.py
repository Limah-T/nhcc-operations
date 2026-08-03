from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from account.models import CustomUser
from directors.models import Director
from core.models import Title

class GeneralBenefits(models.Model):
    description = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    ordering = ["display_order", "description"]

class Benefits(models.Model):
    category = models.CharField(max_length=255)
    description = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    ordering = ["display_order", "description"]
      
class Category(models.Model):
    class Type(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        CORPORATE = "corporate", "Corporate"

    application_type = models.CharField(
        max_length=255, choices=Type.choices, 
        default=Type.CORPORATE 
    )
    annual_fee = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    general_benefit = models.ForeignKey(
        GeneralBenefits, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name="categories"
    )
    benefit = models.ForeignKey(
        Benefits, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name="categories"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AssociatedHungarianCompany(models.Model):
    company_name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        
class MembershipRequiredDocument(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="required_documents"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

class GeneralApplication(models.Model):
    proposer = models.ForeignKey(
        Director, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="proposed_membership_applications"
    )
    proposer_name = models.CharField(max_length=255)
    other_business_interests = models.TextField(null=True, blank=True)
    interest_in_hungary = models.TextField(null=True, blank=True)
    main_challenges = models.TextField(blank=True)
    areas_chamber_can_assist = models.TextField(blank=True)
    declaration_accepted = models.BooleanField(default=False)


class MembershipApplication(models.Model):

    class ApplicationType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        CORPORATE = "corporate", "Corporate"

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SUSPENDED = "suspended", "Suspended"

    application_type = models.CharField(
        max_length=20, choices=ApplicationType.choices
    )
    general = models.OneToOneField(
        GeneralApplication, on_delete=models.PROTECT,
        related_name="membership_application"
    )
    associated_hungarian_company = models.ForeignKey(
        AssociatedHungarianCompany,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="membership_applications"
    )
    application_number = models.CharField(
        max_length=50, unique=True,
        editable=False, null=True, blank=True
    )
    reviewed_by_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="reviewed_applications"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.SUBMITTED
    )
    reviewed_by = models.CharField(max_length=255, blank=True)
    rejection_reason = models.TextField(blank=True)
    date_joined = models.DateField(null=True, blank=True)

class IndividualApplication(models.Model):
    registered_business_name = models.CharField(
        max_length=255, null=True, blank=True)
    office_telephone = PhoneNumberField(null=True, blank=True)
    type_of_business = models.CharField(null=True, blank=True)
    membership_application = models.OneToOneField(
        MembershipApplication, on_delete=models.PROTECT,
        related_name="individual_applications"
    )

class CorporateApplication(models.Model):
    company_name = models.CharField(max_length=255, blank=True)
    company_telephone = PhoneNumberField(null=True, blank=True)
    company_email = models.EmailField(null=True, blank=True)
    company_address = models.TextField(blank=True)
    core_business = models.TextField(blank=True)
    business_type = models.CharField(max_length=255, blank=True)
    holding_company = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=150, blank=True)
    number_of_employees = models.PositiveIntegerField(
        null=True, blank=True
    )
    year_established = models.PositiveIntegerField(
        null=True, blank=True
    )
    website = models.URLField(blank=True)
    membership_application = models.OneToOneField(
        MembershipApplication, on_delete=models.PROTECT,
        related_name="corporate_applications"
    )


class Profile(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.SET_NULL,
        null=True, blank=True,
    ) 
    nationality = CountryField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True, unique=True)  
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Member(models.Model):
    profile = models.OneToOneField(
        Profile, on_delete=models.PROTECT, 
    )
    application = models.ForeignKey(
        MembershipApplication, on_delete=models.PROTECT,
        related_name="members"
    )

class MemberRepresentative(models.Model):
    """Only for the corporate category."""

    class RepresentativeType(models.TextChoices):
        PRIMARY = "primary", "Primary"
        ALTERNATIVE = "alternative", "Alternative"

    profile = models.OneToOneField(
        Profile, on_delete=models.PROTECT, 
    )
    representative_type = models.CharField(
        max_length=20,
        choices=RepresentativeType.choices,
        default=RepresentativeType.ALTERNATIVE
    )
    application = models.ForeignKey(
        MembershipApplication,
        on_delete=models.PROTECT, related_name="representatives"
    )
    position = models.CharField(max_length=255)
    date_joined = models.DateField(blank=True)

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "application",
                    "representative_type"
                ],
                name=(
                    "unique_representative_"
                    "type_per_application"
                )
            )
        ]

class MembershipApplicationDocument(models.Model):
    application = models.ForeignKey(
        MembershipApplication,
        on_delete=models.PROTECT,
        related_name="documents"
    )
    document_type = models.ForeignKey(
        MembershipRequiredDocument,
        on_delete=models.PROTECT,
        related_name="uploaded_documents"
    )
    file = models.FileField(
        upload_to=("membership/documents/%Y/%m/")
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True,blank=True)
    verified_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name=("verified_membership_documents")
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=["application", "document_type"],
                name=(
                    "unique_document_type_"
                    "per_application"
                )
            )

        ]