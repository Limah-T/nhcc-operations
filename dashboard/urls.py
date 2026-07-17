from django.urls import path
from .views import (
    Dashboard, OfficeExpenseDashboard,
    
)

urlpatterns = [
    path("home", Dashboard.as_view(), name="dashboard"),
    path(
        "expense", OfficeExpenseDashboard.as_view(), name="expense-dashboard"
    ),
]