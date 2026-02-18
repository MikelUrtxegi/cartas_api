from rest_framework import serializers
from .models import Session, Group, Vote, Canvas


class SessionCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source="created", read_only=True)
    updated_at = serializers.DateTimeField(source="modified", read_only=True)

    class Meta:
        model = Session
        fields = ["id", "company", "language", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "created_at", "updated_at"]


class GroupCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source="created", read_only=True)
    updated_at = serializers.DateTimeField(source="modified", read_only=True)

    class Meta:
        model = Group
        fields = ["id", "session", "name", "join_code", "created_at", "updated_at"]
        read_only_fields = ["id", "join_code", "created_at", "updated_at"]


class JoinGroupSerializer(serializers.Serializer):
    join_code = serializers.CharField(max_length=12)


class VoteCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source="created", read_only=True)
    updated_at = serializers.DateTimeField(source="modified", read_only=True)

    class Meta:
        model = Vote
        fields = ["id", "session", "group", "card", "value", "comment", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CanvasUpsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Canvas
        fields = ["session", "data"]
