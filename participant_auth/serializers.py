from rest_framework import serializers


class ParticipantJoinSerializer(serializers.Serializer):
    join_code = serializers.CharField(max_length=20)
    nickname = serializers.CharField(max_length=80, required=False, allow_blank=True)
