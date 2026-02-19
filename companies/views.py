from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Company
from .serializers import CompanySerializer

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def companies_dashboard(request):
    if request.method == "GET":
        qs = Company.objects.order_by("-id")
        return Response(CompanySerializer(qs, many=True).data)

    serializer = CompanySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    company = serializer.save(created_by=request.user)
    return Response(CompanySerializer(company).data, status=status.HTTP_201_CREATED)
