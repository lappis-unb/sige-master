from datetime import timedelta

from django.db import models
from django.db.models import Count, Q
from django.utils import timezone

from apps.organizations.models import Entity


class TransductorQuerySet(models.QuerySet):
    def entity(self, *args, **kwargs):
        entity_id = kwargs.get("id", None)
        include_descendants = kwargs.get("inc_desc", True)
        max_depth = kwargs.get("depth", None)

        if not include_descendants:
            return self.filter(located_id=entity_id)

        entity = Entity.objects.filter(id=entity_id).first()
        if not entity:
            return self.none()

        entities = entity.get_descendants(include_self=True, max_depth=max_depth)
        return self.filter(located__in=entities)


class TransductorsManager(models.Manager):
    def get_queryset(self):
        return TransductorQuerySet(self.model, using=self._db)

    def entity(self, *args, **kwargs):
        return self.get_queryset().entity(*args, **kwargs)

    def status(self, status):
        return self.get_queryset().filter(
            status_history__status=status,
            status_history__end_time__isnull=True,
        )

    def active(self):
        return self.get_queryset().filter(
            status_history__status=1,  # models.Status.ACTIVE, (circular imports)
            status_history__end_time__isnull=True,
        )

    def broken(self):
        return self.get_queryset().filter(
            status_history__status=2,  # models.Status.BROKEN (circular imports)
            status_history__end_time__isnull=True,
        )

    def non_status(self):
        return self.get_queryset().filter(status_history__isnull=True)

    def broken_and_non_status(self):
        return self.get_queryset().filter(
            Q(status_history__status=2, status_history__end_time__isnull=True) | Q(status_history__isnull=True)
        )

    def recent_updates(self, days=7):
        return self.get_queryset().filter(
            status_history__end_time__isnull=False,
            status_history__end_time__gte=timezone.now() - timedelta(days=days),
        )

    def history(self, status):
        return self.get_queryset().filter(
            status_history__status=status,
            status_history__end_time__isnull=True,
        )

    def count_by_status(self):
        return (
            self.get_queryset()
            .values("status_history__status")
            .annotate(
                count=Count("status_history__status"),
            )
        )
