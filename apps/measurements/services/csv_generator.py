import csv
import logging
from io import StringIO

from django.http import HttpResponse

logger = logging.getLogger("apps.measurements.services.csv_generator")


class CSVGenerator:
    def __init__(self, queryset, fields=None):
        self.queryset = queryset
        self.fields = fields

    def generate_csv(self):
        csv_file = StringIO()
        csv_writer = csv.writer(csv_file)

        if not self.fields:
            self.fields = [field.name for field in self.queryset.model._meta.fields]

        csv_writer.writerow(self.fields)

        for instance in self.queryset:
            row = []
            for field in self.fields:
                value = getattr(instance, field)
                if hasattr(value, "isoformat"):
                    value = value.isoformat()
                elif isinstance(value, str):
                    value = value.encode("utf-8")
                row.append(value)
            csv_writer.writerow(row)

        csv_file.seek(0)
        return csv_file.getvalue()


def generate_csv_response(queryset, fields=None, filename=None):
    csv_generator = CSVGenerator(queryset)
    csv_data = csv_generator.generate_csv()

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=instant_measurements.csv"
    return response
