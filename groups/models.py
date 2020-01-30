from django.db import models
from rest_framework.exceptions import NotAcceptable
from django.utils.translation import gettext_lazy as _


class GroupType(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        verbose_name=_('Name'),
        help_text=_('This field is required')
    )

    class Meta:
        verbose_name = _('Grouping type')

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        groups_associated = self.group_set.all()

        if not groups_associated:
            super(GroupType, self).delete(*args, **kwargs)
        else:
            exception = NotAcceptable(
                'Is not possible delete this type '
                'because there are groups associated. '
                'Please, delete all transductors associated '
                'with this group.'
            )
            raise exception


class Group(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        verbose_name=_('Name'),
        help_text=_('This field is required')
    )
    type = models.ForeignKey(
        GroupType,
        on_delete=models.CASCADE,
        verbose_name=_('Type'),
        help_text=_('This field is required')
    )

    class Meta:
        verbose_name = _('Grouping')

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        transductors_associated = self.energytransductor_set.all()

        if not transductors_associated:
            super(Group, self).delete(*args, **kwargs)
        else:
            exception = NotAcceptable(
                'Is not possible delete this group '
                'because there are transductors associated.'
                'Please, delete all groups associated '
                'with this group type.'
            )
            raise exception
