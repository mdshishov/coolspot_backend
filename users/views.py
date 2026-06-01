from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer, extend_schema_view
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
)
from phonenumber_field.phonenumber import to_python
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .serializers import (
    CustomTokenObtainPairSerializer,
    ClientRegisterSerializer,
    ClientPhoneCheckSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    LoginResponseSerializer,
    ProfileResponseSerializer,
    ProfileUpdateSerializer,
    DeactivateProfileSerializer,
)

User = get_user_model()


@extend_schema(
    summary="Проверка существования телефона клиента",
    request=ClientPhoneCheckSerializer,
    responses=inline_serializer(
        name="ClientPhoneCheckResponse",
        fields={
            "exists": serializers.BooleanField(),
        },
    ),
)
class ClientPhoneCheckView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClientPhoneCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = to_python(
            serializer.validated_data["phone"],
            region="RU",
        )

        exists = User.objects.filter(phone=phone).filter(role=User.Role.CLIENT).exists()

        return Response(
            {
                "exists": exists,
            }
        )


@extend_schema(
    summary="Регистрация учётной записи клиента",
)
class ClientRegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ClientRegisterSerializer


@extend_schema(
    summary="Вход по логину или телефону",
    responses=LoginResponseSerializer,
)
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    summary="Изменение пароля профиля",
    request=ChangePasswordSerializer,
    responses=inline_serializer(
        name="ChangePasswordResponse",
        fields={
            "detail": serializers.CharField(),
        },
    ),
)
class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.password_changed_at = timezone.now()

        user.save(
            update_fields=[
                "password",
                "password_changed_at",
            ]
        )

        return Response({"detail": "Пароль успешно изменён"})


@extend_schema_view(
    get=extend_schema(
        summary="Информация о текущем пользователе",
        responses=ProfileSerializer,
    ),
    patch=extend_schema(
        summary="Обновление данных профиля",
        request=ProfileUpdateSerializer,
        responses=ProfileSerializer,
    ),
)
class ProfileView(RetrieveUpdateAPIView):
    http_method_names = ["get", "patch"]
    serializer_class = ProfileSerializer

    def get_object(self):
        return User.objects.annotate(
            cart_items_count=Coalesce(
                Sum("cart__positions__quantity"),
                Value(0),
            )
        ).get(pk=self.request.user.pk)

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ProfileUpdateSerializer

        return ProfileSerializer

@extend_schema(
    summary="Деактивация профиля",
    request=DeactivateProfileSerializer,
)
class DeactivateProfileView(APIView):
    def post(self, request):
        serializer = DeactivateProfileSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        user = request.user
        user.is_active = False
        user.password_changed_at = timezone.now()

        user.save(
            update_fields=[
                "is_active",
                "password_changed_at",
            ]
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
