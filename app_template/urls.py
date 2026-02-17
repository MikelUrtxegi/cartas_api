from django.urls import path
from .views import example_endpoint

urlpatterns = [
    path("example/", example_endpoint, name="example"),
]
