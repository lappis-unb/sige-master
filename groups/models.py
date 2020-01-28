from django.db import models
from rest_framework.exceptions import NotAcceptable


class GroupType(models.Model):
    name = models.CharField(primary_key=True, max_length=50)

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
    name = models.CharField(primary_key=True, max_length=50)
    type = models.ForeignKey(GroupType, on_delete=models.CASCADE)

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
