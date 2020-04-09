from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class GroupsConfig(AppConfig):
    name = 'groups'
    verbose_name = _('Meter group module')
