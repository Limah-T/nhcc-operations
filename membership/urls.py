from django.urls import path
from .views.application_views import MembershipApplicationSubmission, Members

urlpatterns = [
    path("overview/", MembershipApplicationSubmission.as_view(), 
        name="membership"),
    path("add/", MembershipApplicationSubmission.as_view(),
        name="add_applications"),
    path("members/", Members.as_view(),
        name="manage_members"),
]