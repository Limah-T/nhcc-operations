from django.urls import path
from .views.role_views import (
    RoleGetCreatetView, RoleUpdateView, RoleDeleteView
)

from .views.staff_views import (
    StaffGetCreateView, StaffUpdateView, StaffDeleteView
)

urlpatterns = [

    path("roles/", RoleGetCreatetView.as_view(), name="roles"),
    path("role/<int:id>/edit/", RoleUpdateView.as_view(), name="edit_role"),
    path("role/<int:id>/delete/", RoleDeleteView.as_view(), name="delete_role"),
    path("roles/delete/", RoleDeleteView.as_view(), name="delete_roles"),

    path("records/", StaffGetCreateView.as_view(), name="staff"),
    path("<int:id>/edit/", StaffUpdateView.as_view(), name="edit_staff"),
    path("<int:id>/delete/", StaffDeleteView.as_view(), name="delete_staff"),
    path("staff/delete/", StaffDeleteView.as_view(), name="delete_staffs"),
]