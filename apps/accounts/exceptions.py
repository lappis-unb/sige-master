from rest_framework.exceptions import APIException


class CantAddUserOtherOrganization(APIException):
    status_code = 403
    default_detail = "Can't add user from another organization"
    default_code = "cant_add_user_other_organization"


class CantAddUserAdmin(APIException):
    status_code = 403
    default_detail = "Can't add user with admin role"
    default_code = "cant_add_user_admin"
