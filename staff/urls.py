from django.urls import path
from .views.role_views import (
    RoleManagementView, RoleUpdateView, 
    RoleDeleteView
)

from .views.staff_views import (
    StaffManagementView,
    StaffUpdateView, StaffDeleteView
)

urlpatterns = [
    path("records/", StaffManagementView.as_view(), name="staff_records"),

    path("roles/", RoleManagementView.as_view(), name="roles"),
    path("role/<int:pk>/edit/", RoleUpdateView.as_view(), name="edit_role"),
    path("role/<int:pk>/delete/", RoleDeleteView.as_view(), name="delete_role"),
    path("roles/delete/", RoleDeleteView.as_view(), name="delete_roles"),

    path("add/", StaffManagementView.as_view(), name="add_staff"),
    path("<int:pk>/edit/", StaffUpdateView.as_view(), name="edit_staff"),
    path("<int:pk>/delete/", StaffDeleteView.as_view(), name="delete_staff"),
    path("staff/delete/", StaffDeleteView.as_view(), name="delete_staffs"),
]