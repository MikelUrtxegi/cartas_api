from django.urls import path
from . import views

urlpatterns = [
    path("sessions/", views.create_session, name="create_session"),
    path("groups/", views.create_group, name="create_group"),
    path("groups/join/", views.join_group, name="join_group"),
    path("votes/", views.create_vote, name="create_vote"),
    path("sessions/<int:session_id>/canvas/", views.canvas_view, name="canvas"),
]
