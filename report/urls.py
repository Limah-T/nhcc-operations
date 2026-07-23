from django.urls import path
from .views import report_view, generate_report

urlpatterns = [
    path("reports/", report_view, name="reports"),
    path("generate/report", generate_report, name="generate_report"),
    

]