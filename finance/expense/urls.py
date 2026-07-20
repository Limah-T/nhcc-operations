from django.urls import path
from .category_views import (
    CategoryView, edit_category, 
    delete_category, delete_categories
)
from .diesel_views import (
    DieselView, edit_diesel, delete_diesel, delete_diesels
)
from .electricity_views import (
    ElectricityView, edit_electricity, 
    delete_electricity, delete_electricities
)
from .expenses_views import (
    ExpenseView, edit_expense, delete_expense, delete_expenses
)

urlpatterns = [
    path(
        "category", CategoryView.as_view(), name="category"
        ),
    path("add/category/", CategoryView.as_view(), name="add-category"),
    path(
        "edit/category/<int:pk>/edit/", edit_category, 
        name="edit_category"
    ),
    path(
        "delete/category<int:pk>/delete/", delete_category, 
        name="delete_category"
    ),
    path(
        "delete/categories/", delete_categories, 
        name="delete_categories"
    ),
    path("diesel", DieselView.as_view(), name="diesel"),
    path("add/diesel/", DieselView.as_view(), name="add_diesel"),
    path("diesel/<int:pk>/edit/", edit_diesel, name="edit_diesel"),
    path("diesel/<int:pk>/delete/", delete_diesel, name="delete_diesel"),
    path("delete/diesels/", delete_diesels, name="delete_diesels"),
    
    path("ekedc", ElectricityView.as_view(), name="electricity"),
    path("add/ekedc/", ElectricityView.as_view(), name="add_electricity"),
    path("ekedc/<int:pk>/edit/", edit_electricity, name="edit_electricity"),
    path("ekedc/<int:pk>/delete/", delete_electricity, name="delete_electricity"),
    path("delete/ekedc/", delete_electricities, name="delete_electricities"),

    path("expense/records/", ExpenseView.as_view(), name="expenses"),
    path("<int:pk>/edit/", edit_expense, name="edit_expense"),
     path("<int:pk>/delete/", delete_expense, name="delete_expense"),
    path("delete/expenses/", delete_expenses, name="delete_expenses"),
]
