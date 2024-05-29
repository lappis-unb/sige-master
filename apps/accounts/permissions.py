from rest_framework import permissions


# Custom permissions
class CustomUserPermissions(permissions.BasePermission):
    # def has_permission(self, request, view):

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Superusuários podem ver qualquer registro
        if user.is_staff:
            return True
        # Gestores podem ver qualquer membro de sua organização
        if hasattr(user, "organization") and user.organization == obj.organization:
            return True

        # Usuários comuns podem ver apenas seu próprio perfil
        return obj == user


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsSuperUserOrAdminCreatingWithinOwnUniversity(permissions.BasePermission):
    def has_permission(self, request, view):
        # Superusuários podem criar qualquer usuário
        if request.user.is_superuser:
            return True

        # Administradores só podem criar usuários comuns e dentro de sua própria universidade
        if request.user.is_staff and not request.data.get("is_superuser"):
            return request.data.get("university") == request.user.university_id
        return False


class UserCreateUpdatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Permitir POST para todos, mas com validações no serializer
        if request.method in ["POST", "PATCH", "PUT"]:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Usuários anônimos não podem atualizar 'role' ou 'organization'
        return not request.user.is_anonymous or "role" not in request.data and "organization" not in request.data


class IsAdminOrSameOrganization(permissions.BasePermission):
    def has_permission(self, request, view):
        # Todos os usuários autenticados podem acessar a view, mas o conteúdo será filtrado mais tarde.
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Superusuários podem ver qualquer registro.
        if request.user.is_superuser:
            return True
        # Gestores só podem ver usuários na mesma organização.
        return obj.organization == request.user.organization
