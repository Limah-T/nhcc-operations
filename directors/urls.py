from django.urls import path
from .views.director_views import (
    directorRecordView
)
from .views.position_views import(
    PositionGetCreateView, PositionUpdateView,
    PositionDeleteView
)
from .views.director_views import (
    DirectorGetCreateView, DirectorUpdateView,
    DirectorDeleteView
)

urlpatterns = [
    path("overview/", directorRecordView, name="director_records"),
    path("position/", PositionGetCreateView.as_view(), name="position"),
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

    path("records", DirectorGetCreateView.as_view(), name="director"),
    path(
        "<int:pk>/edit/", 
        DirectorUpdateView.as_view(), name="edit_director"
    ),
    path(
        "<int:pk>/delete/", 
        DirectorDeleteView.as_view(), name="delete_director"
        ),
    path(
        "delete/", 
        DirectorDeleteView.as_view(), name="delete_directors"
        ),
]