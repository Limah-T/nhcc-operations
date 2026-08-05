from django.urls import path
from .views.category_views import (
    CategoryGetCreateView, CategoryUpdateView, CategoryDeleteView
)
from .views.diesel_views import (
    DieselGetCreateView, DieselUpdateView, DieselDeleteView
)
from .views.electricity_views import (
    EkedcGetCreateView, EkedcUpdateView, EkedcDeleteView,
)
from .views.expenses_views import (
    ExpenseGetCreateView, expenseOverview, 
    ExpenseUpdateView, ExpenseDeleteView, 
)


urlpatterns = [
    path("category/", CategoryGetCreateView.as_view(), name="category"),
    path("category/<int:id>/edit/", CategoryUpdateView.as_view(), name="edit_category"),
    path("category/<int:id>/delete/", CategoryDeleteView.as_view(), name="delete_category"),
    path("delete/categories/", CategoryDeleteView.as_view(), name="delete_categories"),

    path("diesel/", DieselGetCreateView.as_view(), name="diesel"),
    path("diesel/<int:id>/edit/", DieselUpdateView.as_view(), name="edit_diesel"),
    path("diesel/<int:id>/delete/", DieselDeleteView.as_view(), name="delete_diesel"),
    path("delete/diesels/", DieselDeleteView.as_view(), name="delete_diesels"),
    
    path("ekedc/", EkedcGetCreateView.as_view(), name="ekedc"),
    path("ekedc/<int:id>/edit/", EkedcUpdateView.as_view(), name="edit_ekedc"),
    path("ekedc/<int:id>/delete/", EkedcDeleteView.as_view(), name="delete_ekedc"),
    path("delete/ekedc/", EkedcDeleteView.as_view(), name="delete_ekedcs"),

    path("overview/", expenseOverview, name="expense_overview"),
    path("records/",  ExpenseGetCreateView.as_view(), name="expenses"),
    path("<int:id>/edit/", ExpenseUpdateView.as_view(), name="edit_expense"),
    path("<int:id>/delete/", ExpenseDeleteView.as_view(), name="delete_expense"),
    path("delete/expenses/", ExpenseDeleteView.as_view(), name="delete_expenses"),
]
