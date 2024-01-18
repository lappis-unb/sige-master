from rest_framework import permissions

from .models import CustomUser


class UserTypePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        '''
            - Caso a identificação do Token estiver funcionando 
            normalmente, será possível apagar os comentários abaixo 
            e realizar os testes com o Token.

        '''

        try:
            type_user = self.get_type_user()

            userid = request.data["userid"]
            user = CustomUser.objects.get(id=userid)
            return user.user_type == type_user
        except KeyError:
            return False
        except CustomUser.DoesNotExist:
            return False

    def get_type_user(self):
        raise NotImplementedError


class CurrentADMINUserOnly(UserTypePermission):
    def get_type_user(self):
        return "admin"


class CurrentRESEARCHNUserOnly(UserTypePermission):
    def get_type_user(self):
        return "researcher"


class CurrentGENERALUserOnly(UserTypePermission):
    def get_type_user(self):
        return "general"
