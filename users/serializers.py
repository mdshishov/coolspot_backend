from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from phonenumber_field.phonenumber import to_python
from rest_framework import serializers

User = get_user_model()

DEFAULT_ERROR_MESSAGES = {
    "required": "Заполните поле",
    "blank": "Заполните поле",
    "invalid": "Некорректное значение",
}

REQUIRED_BLANK_ERROR_MESSAGES = {
    "required": DEFAULT_ERROR_MESSAGES["required"],
    "blank": DEFAULT_ERROR_MESSAGES["blank"],
}


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["role"] = user.role
        token["pwd_ts"] = int(user.password_changed_at.timestamp())

        return token

    def validate(self, attrs):
        username = attrs.get("username")

        user_obj = User.objects.filter(username=username).first()

        if not user_obj:
            phone = to_python(username, region="RU")

            if phone and phone.is_valid():
                user_obj = User.objects.filter(phone=phone).first()

                if user_obj:
                    attrs["username"] = user_obj.username

        data = super().validate(attrs)
        data["role"] = self.user.role
        return data


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    role = serializers.CharField()


class ClientPhoneCheckSerializer(serializers.Serializer):
    phone = PhoneNumberField(region="RU", error_messages=DEFAULT_ERROR_MESSAGES)


class ClientRegisterSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField(region="RU", error_messages=DEFAULT_ERROR_MESSAGES)
    full_name = serializers.CharField(error_messages=DEFAULT_ERROR_MESSAGES)
    password = serializers.CharField(
        write_only=True, error_messages=REQUIRED_BLANK_ERROR_MESSAGES
    )

    class Meta:
        model = User
        fields = (
            "phone",
            "full_name",
            "password",
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User(
            phone=validated_data["phone"],
            full_name=validated_data["full_name"],
            role=User.Role.CLIENT,
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_old_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль")

        return value

    def validate_new_password(self, value):
        user = self.context["request"].user

        if user.check_password(value):
            raise serializers.ValidationError(
                "Новый пароль должен отличаться от текущего"
            )

        try:
            validate_password(value, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)

        return value


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "full_name",
            "email",
            "phone",
        )

class ProfileReponseSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    cart_items_count = serializers.IntegerField()
