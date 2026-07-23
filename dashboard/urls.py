from django.urls import path
from .views import Dashboard

urlpatterns = [
    path("home", Dashboard.as_view(), name="dashboard"),
]