from django.urls import path
from .views import AskAssistant

urlpatterns = [
    path("ask/", AskAssistant.as_view(), name="ask_ai")
]