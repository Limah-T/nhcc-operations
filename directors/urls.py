from django.urls import path
from .views.director_views import (
    directorRecordView
)
from .views.position_views import(
    PositionGetCreateView, PositionUpdateView,
    PositionDeleteView
)

urlpatterns = [
    path("records/", directorRecordView, name="director_records"),
    path("add/position/", PositionGetCreateView.as_view(), name="position"),
    path(
        "position/<int:pk>/edit/", 
        PositionUpdateView.as_view(), name="edit_position"
    ),
    path(
        "position/<int:pk>/delete/", 
        PositionDeleteView.as_view(), name="delete_position"
        ),
    path(
        "positions/delete/", 
        PositionDeleteView.as_view(), name="delete_positions"
        ),
]