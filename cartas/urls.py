"""
URL configuration for cartas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # JWT (login/refresh)
    path("api/auth/", include("jwt_auth.urls")),

    # Health
    path("", include("health.urls")),

    # API general (ping y futuros)
    path("api/", include("api.urls")),

    # Auth corporativa
    path("api/corp-auth/", include("auth_template.urls")),
]


