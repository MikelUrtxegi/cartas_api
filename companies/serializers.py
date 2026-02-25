from .models import Company
from rest_framework import serializers



class CompanyCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source="created", read_only=True)
    updated_at = serializers.DateTimeField(source="modified", read_only=True)

    class Meta:
        model = Company
        fields = ["id", "name", "description", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id, created_at", "updated_at"]
