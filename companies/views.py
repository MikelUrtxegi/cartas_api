from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Company
from .serializers import CompanyCreateSerializer


def _is_admin(user):
    return bool(user and user.is_authenticated and user.is_staff)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_company(request):
    if not _is_admin(request.user):
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    serializer = CompanyCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    company = serializer.save(created_by=request.user)
    return Response(CompanyCreateSerializer(company).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_companies(request):
    if not _is_admin(request.user):
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    qs = Company.objects.filter(is_active=True).order_by("-id")
    serializer = CompanyCreateSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)