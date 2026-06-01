from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        token_pwd_ts = validated_token.get("pwd_ts")
        current_pwd_ts = int(user.password_changed_at.timestamp())

        if token_pwd_ts != current_pwd_ts:
            raise AuthenticationFailed("Пароль был изменён, необходимо выполнить вход повторно")

        return user
