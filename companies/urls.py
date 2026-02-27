from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_companies, name="dashboard_companies_list"),   # GET
    path("create/", views.create_company, name="dashboard_companies_create"),  # POST
]