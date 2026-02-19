from rest_framework import serializers
from .models import Card

class CardSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source="created", read_only=True)
    updated_at = serializers.DateTimeField(source="modified", read_only=True)

    class Meta:
        model = Card
        fields = ["id", "company", "title", "description", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
