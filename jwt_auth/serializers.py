from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class EmailTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            raise serializers.ValidationError(
                {"detail": "No active account found with the given credentials"}
            )

        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is disabled"})

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "No active account found with the given credentials"}
            )

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
