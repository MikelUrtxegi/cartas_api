from drf_yasg import openapi
from .serializers import UserSerializer

login_response = {
    200: "OK",
    400: "BAD REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT FOUND",
}

password_reset_request_response = {
    201: "CREATED",
    400: "BAD REQUEST",
    429: "TOO MANY REQUESTS",
    500: "INTERNAL SERVER ERROR",
}

reset_token_verification_response = {
    200: "OK",
    400: "BAD REQUEST",
}

password_reset_response = {
    200: "OK",
    400: "BAD REQUEST",
    500: "INTERNAL SERVER ERROR",
}

password_reset_verification_response = {
    200: "OK",
    400: "BAD REQUEST",
    403: "FORBIDDEN",
}

change_password_response = {
    200: "OK",
    400: "BAD REQUEST",
}

get_user_list_response = {
    200: openapi.Response(
        description="Lista de usuarios.",
        schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "email": openapi.Schema(type=openapi.TYPE_STRING),
                    "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "username": openapi.Schema(type=openapi.TYPE_STRING),
                    "is_staff": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                },
            ),
        ),
        examples={
            "application/json": [
                {
                    "id": 1,
                    "email": "user1@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "is_staff": False,
                },
                {
                    "id": 2,
                    "email": "user2@example.com",
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "username": "janedoe",
                    "is_staff": True,
                },
            ]
        },
    ),
    400: "BAD REQUEST",
    403: "FORBIDDEN",
    404: "NOT FOUND",
}

user_creation_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "username": openapi.Schema(type=openapi.TYPE_STRING, example="jane_doe"),
        "first_name": openapi.Schema(type=openapi.TYPE_STRING, example="Jane"),
        "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="Doe"),
        "email": openapi.Schema(type=openapi.TYPE_STRING, example="janedoe@email.com"),
        "telephone": openapi.Schema(type=openapi.TYPE_STRING, example="655444333"),
    },
    required=["username", "first_name", "last_name", "email"],
)

user_creation_response = {201: "CREATED", 400: "BAD REQUEST", 403: "FORBIDDEN"}

user_detail_response = {
    200: openapi.Response(
        description="Detalles del usuario.",
        schema=UserSerializer,
        examples={
            "application/json": {
                "id": 1,
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "is_staff": False,
                "verified": True,
                "phone": "123-456-7890",
                "login_count": 5,
                "is_deleted": False,
                "deleted_at": "null",
                "profile_image": "http://example.com/media/profile_images/uuid.jpg",
            }
        },
    ),
    400: "BAD REQUEST",
    403: "FORBIDDEN",
    404: "NOT FOUND",
}

user_edit_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "username": openapi.Schema(type=openapi.TYPE_STRING, example="jane_doe"),
        "first_name": openapi.Schema(type=openapi.TYPE_STRING, example="Jane"),
        "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="Doe"),
        "email": openapi.Schema(type=openapi.TYPE_STRING, example="janedoe@email.com"),
        "telephone": openapi.Schema(type=openapi.TYPE_STRING, example="655444333"),
    },
)

user_delete_response = {204: "NO CONTENT", 403: "FORBIDDEN"}
