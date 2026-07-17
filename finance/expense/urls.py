from django.urls import path
from .category_views import (
    CategoryView, edit_category, delete_category, delete_categories
)
from .diesel_views import (
    DieselView, edit_diesel, delete_diesel, delete_diesels
)
from .electricity_views import (
    ElectricityView, edit_electricity, delete_electricity, delete_electricities
)

urlpatterns = [
    path(
        "category", CategoryView.as_view(), name="category"
        ),
    path(
        "add/category/", CategoryView.as_view(),
        name="add-category"
    ),
    path(
        "edit/category/<int:pk>/edit/", edit_category, name="edit_category"
    ),
    path(
        "delete/category<int:pk>/delete/", delete_category, name="delete_category"
    ),
    path(
        "delete/categories/", delete_categories, name="delete_categories"
    ),
    path(
        "diesel", DieselView.as_view(), name="diesel"
    ),
    path(
        "add/diesel/", DieselView.as_view(), name="add_diesel"
    ),
    path(
        "edit/diesel/<int:pk>/edit/", edit_diesel, name="edit_diesel"
    ),
    path(
        "delete/diesel/<int:pk>/delete/", delete_diesel, name="delete_diesel"
    ),
    path(
        "delete/diesels/", delete_diesels, name="delete_diesels"
    ),
    path(
        "electricity", ElectricityView.as_view(), name="electricity"
    ),
    path(
        "add/electricity/", ElectricityView.as_view(), name="add-electricity"
    ),
    path(
        "edit/electricity/<int:pk>/edit/", edit_electricity, name="edit_electricity"
    ),
    path(
        "delete/electricity/<int:pk>/delete/", delete_electricity, name="delete_electricity"
    ),
    path(
        "delete/electricities/", delete_electricities, name="delete_electricities"
    ),
]
