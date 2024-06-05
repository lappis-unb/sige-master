import logging

logger = logging.getLogger("apps")


class DynamicFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)
        user = self.context["request"].user

        if user.is_anonymous:
            logger.info("User is anonymous")
            self.fields.pop("is_superuser", None)
            self.fields.pop("organization", None)
            self.fields.pop("role", None)
            self.fields.pop("is_admin", None)
            self.fields.pop("is_staff", None)
            self.fields.pop("is_member", None)
            self.fields.pop("is_approved", None)
            self.fields.pop("is_active", None)
            self.fields.pop("is_deleted", None)
            self.fields.pop("date_joined", None)
            self.fields.pop("last_login", None)
            self.fields.pop("groups", None)
            self.fields.pop("user_permissions", None)
            self.fields.pop("id", None)
            self.fields.pop("username", None)
            self.fields.pop("first_name", None)
            self.fields.pop("last_name", None)
            self.fields.pop("phone_number", None)
            self.fields.pop("is_approved", None)
