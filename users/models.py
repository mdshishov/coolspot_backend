import re
from phonenumber_field.modelfields import PhoneNumberField

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager

from users.validators import validate_client_name


class CustomUserManager(UserManager):
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("role", CustomUser.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username=username, password=password, **extra_fields)

    def create_user(self, username=None, password=None, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    objects = CustomUserManager()

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    class Role(models.TextChoices):
        CLIENT = "client", "Клиент"
        STAFF = "staff", "Сотрудник"
        ADMIN = "admin", "Администратор"

    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Логин",
        help_text="Для клиента может быть сгенерировано автоматически на основе его номера телефона",
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email",
    )
    phone = PhoneNumberField(
        unique=True,
        blank=True,
        null=True,
        region="RU",
        verbose_name="Телефон",
        help_text="Обязательное поле для клиента",
    )
    full_name = models.CharField(
        "Имя",
        max_length=255,
        blank=True,
        null=True,
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
        verbose_name="Роль",
    )
    is_active = models.BooleanField(
        "Активен",
        default=True,
    )
    is_staff = models.BooleanField(
        "Сотрудник",
        default=False,
    )
    is_superuser = models.BooleanField(
        "Суперпользователь",
        default=False,
    )
    password_changed_at = models.DateTimeField(
        "Последнее изменение пароля",
        auto_now_add=True,
    )
    date_joined = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    def __str__(self):
        if self.full_name:
            return f"{self.username} ({self.full_name})"
        return self.username

    @property
    def is_client_role(self):
        return self.role == CustomUser.Role.CLIENT

    @property
    def is_staff_role(self):
        return self.role == CustomUser.Role.STAFF

    def clean(self):
        if self.role == self.Role.CLIENT and not self.phone:
            if not self.phone:
                raise ValidationError({"phone": "Телефон обязателен для клиента"})
        if not self.full_name:
            raise ValidationError({"full_name": "Имя обязательно для клиента"})

        try:
            validate_client_name(self.full_name)
        except ValidationError as e:
            raise ValidationError({"full_name": e.messages})
        super().clean()

    def save(self, *args, **kwargs):
        self.is_staff = self.role in (self.Role.STAFF, self.Role.ADMIN)
        self.is_superuser = self.role == self.Role.ADMIN

        if self.role == self.Role.CLIENT and not self.username:
            self.username = self.generate_username()

        super().save(*args, **kwargs)

    def generate_username(self):
        phone = re.sub(r"\D", "", str(self.phone))
        return f"client_{phone}"
