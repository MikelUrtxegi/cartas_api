from django.urls import path, include
from . import views

urlpatterns = [
    path("companies/", include("companies.urls")),
    path("cards/", include("cards.urls")),
    path("decks/", include("decks.urls")),
    
    path("sessions/", views.list_sessions, name="list_sessions"),
    path("sessions/<int:session_id>/", views.session_detail, name="session_detail"),
    path("sessions/<int:session_id>/groups/", views.session_groups, name="session_groups"),
    path("sessions/<int:session_id>/votes/", views.session_votes, name="session_votes"),
]
