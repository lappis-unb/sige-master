import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.locations.models import Address, GeographicLocation

logger = logging.getLogger("apps")


class EntityType(models.IntegerChoices):
    UNIVERSITY = 1, _("University")
    CAMPUS = 2, _("Campus")
    INSTITUTE = 3, _("Institute")
    FACULTY = 4, _("Faculty")
    SCHOOL = 5, _("School")
    DEPARTMENT = 6, _("Department")
    DIVISION = 7, _("Division")
    BUILDING = 8, _("Building")
    FLOOR = 9, _("Floor")
    CLASSROOM = 10, _("Classroom")
    LABORATORY = 11, _("Laboratory")
    OTHER = 12, _("Other")


class Entity(models.Model):
    name = models.CharField(max_length=255, blank=False)
    acronym = models.CharField(max_length=16, blank=False, unique=True)
    description = models.CharField(max_length=255, blank=True)
    entity_type = models.PositiveSmallIntegerField(choices=EntityType.choices)
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        "self",
        related_name="children",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    geo_location = models.ForeignKey(
        GeographicLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")

    def __str__(self):
        return self.get_hierarchy_str()

    def is_root_entity(self):
        return self.parent is None

    def get_children(self):
        return self.children.all()  # using related_name
        # return Entity.objects.filter(parent=self)

    def get_hierarchy(self, is_reversed=False, head=True):
        hierarchy = [f"{self.acronym} ({self.name})"] if head else [self.acronym]
        if self.parent:
            hierarchy.extend(self.parent.get_hierarchy(head=head))
        return hierarchy.reverse() if is_reversed else hierarchy

    def get_hierarchy_str(self, is_reversed=False, head=False):
        return "  -->  ".join(self.get_hierarchy())

    def get_descendants(self, include_self=False, max_depth=None, depth=0):
        descendants = [self] if include_self else []
        children = self.children.all()
        if max_depth and depth >= max_depth or not children:
            return descendants

        for child in children:
            descendants.append(child)
            descendants.extend(child.get_descendants(max_depth=max_depth, depth=depth + 1))
        return descendants


class Organization(Entity):
    cnpj = models.CharField(max_length=14, blank=False, unique=True)
    website = models.URLField(max_length=255, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    def __str__(self):
        return f"{self.acronym} - {self.name}"
