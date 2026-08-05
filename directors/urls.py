from django.urls import path

from .views.position_views import(
    PositionGetCreateView, PositionUpdateView,
    PositionDeleteView
)
from .views.director_views import (
    DirectorGetCreateView, DirectorUpdateView,
    DirectorDeleteView
)

urlpatterns = [
    path("position/", PositionGetCreateView.as_view(), name="position"),
    path(
        "position/<int:id>/edit/", 
        PositionUpdateView.as_view(), name="edit_position"
    ),
    path(
        "position/<int:id>/delete/", 
        PositionDeleteView.as_view(), name="delete_position"
        ),
    path(
        "positions/delete/", 
        PositionDeleteView.as_view(), name="delete_positions"
        ),

    path("", DirectorGetCreateView.as_view(), name="directors"),
    path(
        "<int:id>/edit/", 
        DirectorUpdateView.as_view(), name="edit_director"
    ),
    path(
        "<int:id>/delete/", 
        DirectorDeleteView.as_view(), name="delete_director"
        ),
    path(
        "delete/", 
        DirectorDeleteView.as_view(), name="delete_directors"
        ),
]