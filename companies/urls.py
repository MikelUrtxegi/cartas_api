from django.urls import path
from .views import companies_dashboard

urlpatterns = [
    path("companies/", companies_dashboard, name="dashboard_companies"),
]
