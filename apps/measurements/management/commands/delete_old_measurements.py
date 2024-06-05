from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.measurements.models import CumulativeMeasurement, InstantMeasurement


class Command(BaseCommand):
    help = "Deletes all measurements older than 30 days"

    def handle(self, *args, **options):
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)

        try:
            InstantMeasurement.objects.filter(slave_collection_date__lt=thirty_days_ago).delete()
            CumulativeMeasurement.objects.filter(collection_date__lt=thirty_days_ago).delete()
            self.stdout.write(self.style.SUCCESS("Measurements older than 30 days have been successfully deleted."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to delete measurements: {str(e)}"))
