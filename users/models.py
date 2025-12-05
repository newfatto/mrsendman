from typing import Any

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Менеджер пользователя с авторизацией по email вместо username.
    Используется моделью CustomUser.
    """

    use_in_migrations: bool = True

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> "CustomUser":
        """
        Создаёт обычного пользователя.

        :param email: email пользователя (обязательный)
        :param password: пароль
        :param extra_fields: дополнительные поля (first_name, last_name и т.п.)
        """
        if not email:
            raise ValueError("У пользователя должен быть указан email")

        email = self.normalize_email(email)
        user: CustomUser = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any) -> "CustomUser":
        """
        Создаёт суперпользователя (админа).

        :param email: email суперпользователя
        :param password: пароль
        :param extra_fields: дополнительные поля
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("У суперпользователя is_staff должно быть True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("У суперпользователя is_superuser должно быть True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # исключаем заполнение поля при создании экземпляра модели
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    USERNAME_FIELD = "email"  # поле будет использовано для авторизации
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]  # обязательные поля, которые должны быть указаны при создании суперпользователя через команду createsuperuser

    objects: CustomUserManager = CustomUserManager()

    def __str__(self):
        return self.email
