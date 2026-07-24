from django.urls import path
from .views import reportOverview, ReportManagementView

urlpatterns = [
    path("reports/", reportOverview, name="reports"),
    path("generate/report", ReportManagementView.as_view(), name="generate_report"),
    
]