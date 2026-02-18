from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from auth_template.serializers import (
    LoginSerializer,
    UserSerializer,
    UserListSerializer,
)
from rest_framework.pagination import PageNumberPagination
from auth_template.models import CustomUser, PasswordResetToken
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from .swagger_schemas import (
    user_creation_request_body,
    user_creation_response,
    login_response,
    password_reset_request_response,
    reset_token_verification_response,
    password_reset_response,
    password_reset_verification_response,
    change_password_response,
    get_user_list_response,
    user_detail_response,
    user_edit_body,
    user_delete_response,
)


class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,
        operation_description="Iniciar sesión con credenciales de usuario.",
        responses=login_response,
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

            try:
                user = CustomUser.objects.get(email=email)
                if user.is_deleted:
                    return Response(
                        {"error": "Este usuario ha sido eliminado."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                if user.check_password(password):
                    if not user.verified:
                        return Response(
                            {"detail": "Debes confirmar tu correo."},
                            status=status.HTTP_401_UNAUTHORIZED,
                        )

                    user.login_count += 1
                    user.last_login = timezone.now()
                    user.save()

                    profile_image_url = None
                    if user.profile_image:
                        profile_image_url = request.build_absolute_uri(
                            user.profile_image.url
                        )

                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                            "profile_image_url": profile_image_url,
                            "is_staff": user.is_staff,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Credenciales inválidas."},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            except CustomUser.DoesNotExist as e:
                # logger.error(f"{e}") -> Implement logger
                return Response(
                    {"error": "Usuario no encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetRequestView(APIView):
    @swagger_auto_schema(
        operation_description="Solicitar restablecimiento de contraseña.",
        responses=password_reset_request_response,
    )
    def post(self, request, *args, **kwargs):
        try:
            reset_attempts = request.session.get("reset_attempts", [])
            thirty_mins_ago = datetime.now() - timedelta(minutes=30)

            recent_attempts = [
                attempt
                for attempt in reset_attempts
                if (
                    datetime.strptime(attempt, "%Y-%m-%dT%H:%M:%S.%f") > thirty_mins_ago
                )
            ]

            if len(recent_attempts) >= 5:
                oldest_attempt = datetime.strptime(
                    recent_attempts[0], "%Y-%m-%dT%H:%M:%S.%f"
                )
                next_allowed_attempt = oldest_attempt + timedelta(minutes=30)
                wait_time = next_allowed_attempt - datetime.now()
                minutes_to_wait = int(wait_time.total_seconds() / 60)
                return Response(
                    {"error": "TOO_MANY_REQUESTS"},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            email = request.data.get("email")

            try:
                email = email.lower()
                user = CustomUser.objects.get(email=email)
                token_record = PasswordResetToken(user=user)
                token_record.save()

                subject = "Restablecer contraseña"
                message = (
                    f"Haga clic en el siguiente enlace para restablecer "
                    f"su contraseña usando el código proporcionado: "
                    f"{settings.URL_SERVER}/recovery-code?token={token_record.token}"
                )
                from_email = "alchemymachinelearning@gmail.com"
                recipient_list = [user.email]

                # Renderiza el HTML y pasa la variable del subdominio
                message_html = render_to_string(
                    "email_templates/reset_password_email.html",
                    {
                        "token": token_record.token,
                        "reset_password_url": f"{settings.URL_SERVER}/recovery-code?token={token_record.token}",
                    },
                )

                send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    html_message=message_html,
                )

                recent_attempts.append(datetime.now().isoformat())
                request.session["reset_attempts"] = recent_attempts
                request.session.modified = True

                return Response(
                    {"detail": "Email sent successfully"},
                    status=status.HTTP_201_CREATED,
                )

            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "EMAIL_NOT_EXISTS"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            # logger.error(f"{e}") -> Implement logger
            print(e, "error")
            return Response(
                {"error": "INTERNAL_SERVER_ERROR"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResetTokenVerificationView(APIView):
    @swagger_auto_schema(
        operation_description="Verificar si el token de restablecimiento es válido.",
        responses=reset_token_verification_response,
    )
    def post(self, request, *args, **kwargs):
        try:
            token = request.data.get("token")
            try:
                token_record = PasswordResetToken.objects.get(token=token)

                if token_record.is_expired():
                    token_record.delete()
                    return Response(
                        {"error": "TOKEN_EXPIRED"}, status=status.HTTP_400_BAD_REQUEST
                    )

                return Response(
                    {"detail": "Token es válido"}, status=status.HTTP_200_OK
                )

            except PasswordResetToken.DoesNotExist:
                return Response(
                    {"error": "INVALID_TOKEN"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(e, "error")
            # logger.error(f"{e}") -> Implement logger


class PasswordResetView(APIView):
    @swagger_auto_schema(
        operation_description="Restablecer contraseña con un token válido.",
        responses=password_reset_response,
    )
    def post(self, request, *args, **kwargs):
        try:
            token = request.data.get("token")
            new_password = request.data.get("new_password")

            try:
                token_record = PasswordResetToken.objects.get(token=token)

                if token_record.is_expired():
                    token_record.delete()
                    return Response(
                        {"error": "TOKEN_EXPIRED"}, status=status.HTTP_400_BAD_REQUEST
                    )

                user = token_record.user
                user.set_password(new_password)
                user.verified = True
                user.save()

                token_record.delete()  # Delete token after use
                return Response(
                    {"detail": "Contraseña restablecida con éxito"},
                    status=status.HTTP_200_OK,
                )
            except PasswordResetToken.DoesNotExist:
                return Response(
                    {"error": "INVALID_TOKEN"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            # logger.error(f"{e}") -> Implement logger
            return Response(
                {"error": "INTERNAL_SERVER_ERROR"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PasswordResetVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Verificar si el usuario puede restablecer la contraseña.",
        responses=password_reset_verification_response,
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_invited:
            return Response(
                {"error": "NOT_INVITED"},
                status=status.HTTP_403_FORBIDDEN,
            )
        password = request.data.get("new_password")
        if not password:
            return Response(
                {"error": "Contraseña requerida"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user.set_password(password)
            user.verified = True
            user.save()
        except Exception as e:
            return Response(
                {"error": "PASSWORD_RESET_ERROR"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            {"detail": "Contraseña restablecida con éxito"}, status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Cambiar la contraseña del usuario.",
        responses=change_password_response,
    )
    def post(self, request, *args, **kwargs):
        try:
            current_password = request.data.get("current_password")
            new_password = request.data.get("new_password")
            username = request.user.username

            user = authenticate(username=username, password=current_password)
            if user:
                user.set_password(new_password)
                user.save()
                return Response(
                    {"changed": True, "detail": "Contraseña actualizada con éxito."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"changed": False, "error": "INVALID PASSWORD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            print(e, "error")
            # logger.error(f"{e}") -> Implement logger


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @swagger_auto_schema(
        operation_description="Obtener la lista de usuarios",
        responses=get_user_list_response,
    )
    def get(self, request):
        if not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para ver esta lista."},
                status=status.HTTP_403_FORBIDDEN,
            )
        search_query = request.query_params.get("search", "")
        page_query = request.query_params.get("page")
        users = CustomUser.objects.filter(is_deleted=False)
        if not users:
            return Response(
                {"error": "No se ha encontrado ningún usuario"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not page_query:
            serializer = UserSerializer(users, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
            )
        users = users.order_by("last_name")
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(users, request)
        if not paginated_users:
            return Response(
                {"error": "No hay usuarios registrados."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserListSerializer(paginated_users, many=True)
        if not users:
            return Response(
                {"error": "No hay usuarios registrados."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Crear un nuevo usuario",
        request_body=user_creation_request_body,
        responses=user_creation_response,
    )
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para crear un usuario."},
                status=status.HTTP_403_FORBIDDEN,
            )
        password = settings.DEFAULT_USER_PASSWORD
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(verified=True, is_staff=False, password=password)
            return Response(
                {"detail": "Usuario creado con éxito."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Obtener un usuario por ID.",
        responses=user_detail_response,
    )
    def get(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para ver este usuario"},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = CustomUser.objects.get(pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Actualizar un usuario por ID.",
        request_body=user_edit_body,
        responses=user_detail_response,
    )
    def put(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para editar este usuario"},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = CustomUser.objects.get(pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Borrar un usuario por ID.",
        responses=user_delete_response,
    )
    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para borrar este usuario"},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = CustomUser.objects.get(pk=pk)
        user.is_deleted = True
        user.deleted_at = timezone.now()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
