from django.urls import path
from .category_views import (
    categoryOverview, CategoryManagementView,
    CategoryUpdateView, CategoryDeleteView
)
from .diesel_views import (
    dieselOverView, DieselManagementView,
    DieselUpdateView, DieselDeleteView
)
from .electricity_views import (
    ekedcOverview, EkedcManagementView, 
    EkedcUpdateView, EkedcDeleteView,
)
from .expenses_views import (
    ExpenseManagementView, expenseOverview, 
    ExpenseUpdateView, ExpenseDeleteView
)


urlpatterns = [
    path("category/overview/", categoryOverview, name="category_overview"),
    path("add/category/", CategoryManagementView.as_view(), name="category"),
    path("category/<int:pk>/edit/", CategoryUpdateView.as_view(), name="edit_category"),
    path("category/<int:pk>/delete/", CategoryDeleteView.as_view(), name="delete_category"),
    path("delete/categories/", CategoryDeleteView.as_view(), name="delete_categories"),

    path("diesel/overview/", dieselOverView, name="diesel_overview"),
    path("add/diesel/", DieselManagementView.as_view(), name="diesel"),
    path("diesel/<int:pk>/edit/", DieselUpdateView.as_view(), name="edit_diesel"),
    path("diesel/<int:pk>/delete/", DieselDeleteView.as_view(), name="delete_diesel"),
    path("delete/diesels/", DieselDeleteView.as_view(), name="delete_diesels"),
    
    path("ekedc", ekedcOverview, name="ekedc_overview"),
    path("add/ekedc/", EkedcManagementView.as_view(), name="ekedc"),
    path("ekedc/<int:pk>/edit/", EkedcUpdateView.as_view(), name="edit_ekedc"),
    path("ekedc/<int:pk>/delete/", EkedcDeleteView.as_view(), name="delete_ekedc"),
    path("delete/ekedc/", EkedcDeleteView.as_view(), name="delete_ekedcs"),

    path("overview/", expenseOverview, name="expense_overview"),
    path("records/",  ExpenseManagementView.as_view(), name="expenses"),
    path("<int:pk>/edit/", ExpenseUpdateView.as_view(), name="edit_expense"),
    path("<int:pk>/delete/", ExpenseDeleteView.as_view(), name="delete_expense"),
    path("delete/expenses/", ExpenseDeleteView.as_view(), name="delete_expenses"),
]
