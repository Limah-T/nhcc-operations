from django.urls import path
from .role_views import (
    staffRecords, roleView, editRoleView,
    deleteRole, deleteRoles
)

from .staff_views import (
    staffView, editStaffView
)

urlpatterns = [
    path("records/", staffRecords, name="staff_records"),
    path("roles/", roleView, name="roles"),
    path("role/<int:pk>/edit/", editRoleView, name="edit_role"),
    path("role/<int:pk>/delete/", deleteRole, name="delete_role"),
    path("roles/delete/", deleteRoles, name="delete_roles"),

    path("/", staffView, name="staff"),
    path("<int:pk>/edit/", editStaffView, name="edit_staff"),
    

]