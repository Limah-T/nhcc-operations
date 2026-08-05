from django.contrib import admin
from django.urls import path, include
from dashboard.views import Dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("account.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("dashboard/expense/", include("finance.expense.urls")),
    path("dashboard/staff/", include("staff.urls")),
    path("dashboard/", include("report.urls")),
    path("template/", include("templating.urls")),
    path("directors/", include("directors.urls")),
    path("membership/", include("membership.urls")),
     # Django Silk
    path("silk/", include("silk.urls", namespace="silk")),
    path("", Dashboard.as_view(), name="dashboard")

]
