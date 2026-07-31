# from django.conf import settings
# from django.db import models

# class MembershipCategory(models.Model):
#     """E.g Corporate, Individual"""
#     name = models.CharField(max_length=100, unique=True)
#     annual_fee = models.DecimalField(max_digits=12, decimal_places=2)
#     description = models.TextField(blank=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class MembershipApplication(models.Model):

#     class Status(models.TextChoices):
#         DRAFT = "draft", "Draft"
#         SUBMITTED = "submitted", "Submitted"
#         UNDER_REVIEW = "under_review", "Under Review"
#         APPROVED = "approved", "Approved"
#         REJECTED = "rejected", "Rejected"
#         SUSPENDED = "suspended", "Suspended"

#     application_number = models.CharField(
#         max_length=50, unique=True, editable=False
#     )
#     category = models.ForeignKey(
#         "MembershipCategory", on_delete=models.PROTECT,
#         related_name="applications"
#     )
#     status = models.CharField(
#         max_length=30, choices=Status.choices, default=Status.DRAFT
#     )
#     applicant_name = models.CharField(max_length=255)
#     registration_number = models.CharField(
#         max_length=100, blank=True
#     )
#     office_address = models.TextField(blank=True)
#     telephone_number = models.CharField(max_length=30)
#     business_type = models.CharField(max_length=255, blank=True)
#     company_name = models.CharField(max_length=255, blank=True)
#     holding_company = models.CharField(max_length=255, blank=True)
#     rc_number = models.CharField(max_length=100, blank=True)
#     number_of_employees = models.PositiveIntegerField(
#         null=True, blank=True
#     )
#     year_established = models.PositiveIntegerField(
#         null=True, blank=True
#     )
#     physical_address = models.TextField(blank=True)
#     postal_address = models.TextField(blank=True)
#     website = models.URLField(blank=True)
#     core_business = models.TextField(blank=True)
#     other_business_interests = models.TextField(blank=True)
#     interest_in_hungary = models.TextField(blank=True)
#     main_challenges = models.TextField(blank=True)
#     areas_chamber_can_assist = models.TextField(blank=True)
#     declaration_accepted = models.BooleanField(default=False)
#     submitted_at = models.DateTimeField(null=True, blank=True)
#     reviewed_at = models.DateTimeField(null=True, blank=True)
#     reviewed_by_user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#         related_name="reviewed_membership_applications"
#     )
#     reviewed_by = models.CharField(max_length=255)
#     rejection_reason = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     date_joined = models.DateTimeField(blank=True)

#     class Meta:

#         ordering = ["date_joined"]

# class MemberDirector(models.Model):

#     application = models.ForeignKey(
#         MembershipApplication,
#         on_delete=models.CASCADE,
#         related_name="directors"
#     )

#     full_name = models.CharField(max_length=255)
#     nationality = models.CharField(max_length=100)
#     position = models.CharField(max_length=150, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)


# class MemberRepresentative(models.Model):

#     class RepresentativeType(models.TextChoices):

#         PRIMARY = "primary", "Primary"

#         ALTERNATIVE = "alternative", "Alternative"

#     application = models.ForeignKey(
#         MembershipApplication,
#         on_delete=models.CASCADE,
#         related_name="representatives"
#     )

#     representative_type = models.CharField(
#         max_length=20, choices=RepresentativeType.choices
#     )

#     full_name = models.CharField(max_length=255)
#     position = models.CharField(max_length=150)
#     office_phone = models.CharField(max_length=30, blank=True)
#     mobile_phone = models.CharField(max_length=30)
#     email = models.EmailField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:

#         constraints = [

#             models.UniqueConstraint(
#                 fields=[
#                     "application",
#                     "representative_type"
#                 ],
#                 name=(
#                     "unique_representative_"
#                     "type_per_application"
#                 )
#             )

#         ]

# class AssociatedHungarianCompany(models.Model):

#     application = models.ForeignKey(
#         MembershipApplication,
#         on_delete=models.CASCADE,
#         related_name="hungarian_companies"
#     )

#     company_name = models.CharField(max_length=255)
#     address = models.TextField()

#     created_at = models.DateTimeField(auto_now_add=True)

# class MembershipBenefit(models.Model):

#     category = models.ForeignKey(
#         MembershipCategory,
#         on_delete=models.CASCADE,
#         related_name="benefits"
#     )

#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     display_order = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True)

#     class Meta:

#         ordering = ["display_order", "title"]

# class MembershipBenefit(models.Model):

#     category = models.ForeignKey(
#         MembershipCategory,
#         on_delete=models.CASCADE,
#         related_name="benefits"
#     )

#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     display_order = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True)

#     class Meta:
#         ordering = ["display_order", "title"]

# class MembershipRequiredDocument(models.Model):

#     title = models.CharField(
#         max_length=255
#     )

#     description = models.TextField(
#         blank=True
#     )

#     is_required = models.BooleanField(
#         default=True
#     )

#     is_active = models.BooleanField(
#         default=True
#     )

#     display_order = models.PositiveIntegerField(
#         default=0
#     )

#     def __str__(self):

#         return self.title

# class MembershipApplicationDocument(models.Model):

#     application = models.ForeignKey(
#         MembershipApplication,
#         on_delete=models.CASCADE,
#         related_name="documents"
#     )

#     document_type = models.ForeignKey(
#         MembershipRequiredDocument,
#         on_delete=models.PROTECT,
#         related_name="uploaded_documents"
#     )

#     file = models.FileField(
#         upload_to=("membership/documents/%Y/%m/")
#     )

#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     verified = models.BooleanField(default=False)
#     verified_at = models.DateTimeField(null=True,blank=True)
#     verified_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#         related_name=(
#             "verified_membership_documents"
#         )
#     )

#     class Meta:

#         constraints = [

#             models.UniqueConstraint(
#                 fields=["application", "document_type"],
#                 name=(
#                     "unique_document_type_"
#                     "per_application"
#                 )
#             )

#         ]
