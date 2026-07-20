from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("account.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("dashboard/expense/", include("finance.expense.urls")),
    path("dashboard/reports/", include("report.urls")),

]
