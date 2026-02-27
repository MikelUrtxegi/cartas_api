from django.urls import path
from .views import participant_join

urlpatterns = [
    path("join/", participant_join, name="participant_join"),
]
