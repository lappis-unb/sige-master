from datetime import timedelta

from django.db import models
from django.utils import timezone


class TransductorsManager(models.Manager):
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
                count=models.Count(
                    "status_history__status",
                )
            )
        )
