from django.urls import path
from .views import MembershipApplicationTemplateView

urlpatterns = [
    path("members/", MembershipApplicationTemplateView.as_view(), 
        name="membership_application")
]