from rest_framework_simplejwt.tokens import RefreshToken


def create_custom_jwt_token(user):
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.get_role_display()
    refresh["is_admin"] = user.is_superuser
    refresh["email"] = user.email

    return {"access": str(refresh.access_token), "refresh": str(refresh)}
