from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.deconstruct import deconstructible
from django.utils import timezone
from datetime import timedelta
import uuid
import os


@deconstructible
class PathAndRename(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        # obtiene la extensión del archivo y genera un UUID
        ext = os.path.splitext(filename)[1]
        # genera un nuevo nombre de archivo con el UUID
        new_filename = "{}{}".format(uuid.uuid4(), ext)
        # retorna la ruta completa del nuevo nombre de archivo
        return os.path.join(self.sub_path, new_filename)


path_and_rename_profile = PathAndRename("profile_images")


def default_expires_at():
    return timezone.now() + timedelta(hours=1)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=40, blank=True, null=True)
    login_count = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    profile_image = models.ImageField(
        upload_to=path_and_rename_profile, blank=True, null=True
    )


class UserSession(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    data = models.JSONField(default=dict)


class PasswordResetToken(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expires_at)

    def is_expired(self):
        return self.expires_at < timezone.now()
