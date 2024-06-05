import logging
from pathlib import Path

from django.utils.deconstruct import deconstructible
from rest_framework import serializers

from apps.memory_maps.modbus.settings import CSV_SCHEMA
from apps.transductors.utils import parse_uploaded_csv_file

logger = logging.getLogger("apps")


def latitude_validator(value):
    if value < -90 or value > 90:
        raise serializers.ValidationError(f"{value} is not a valid latitude")


def longitude_validator(value):
    if value < -180 or value > 180:
        raise serializers.ValidationError(f"{value} is not a valid longitude")


@deconstructible
class CsvFileValidator:
    def __init__(self, allowed_extensions=None, max_size=None):
        self.allowed_extensions = allowed_extensions or ["csv"]
        self.max_size = max_size or 102_400  # 100 kilobytes

    def __call__(self, value):
        self._validate_file_extension(value.name)
        self._validade_file_size(value.size)
        self._validate_fields(value)

    def _validate_file_extension(self, file_name):
        file_extension = Path(file_name).suffix[1:].lower()
        if file_extension not in self.allowed_extensions:
            raise serializers.ValidationError(f"Invalid file type '.{file_extension}'. Only CSV files are accepted.")

    def _validade_file_size(self, file_size):
        if self.max_size and file_size > self.max_size:
            raise serializers.ValidationError(
                f"File size is '{(file_size / 1024):.2f} kbytes', but should not exceed {self.max_size // 1024} kbytes"
            )

    def _validate_fields(self, file):
        csv_reader = parse_uploaded_csv_file(file)

        try:
            headers = set(csv_reader[0].keys())
        except Exception:
            raise serializers.ValidationError("Invalid CSV. No headers in first line")

        missing_headers = set(CSV_SCHEMA) - headers

        if missing_headers:
            raise serializers.ValidationError(f"Invalid CSV no required headers. Missing headers: {missing_headers}")

        for row in csv_reader:
            for key, value in row.items():
                if key not in CSV_SCHEMA:
                    continue

                if value == "":
                    raise serializers.ValidationError(f"Field [{key} : {value}] value cannot be null.")

                column_type = CSV_SCHEMA.get(key)
                try:
                    column_type(value)
                except ValueError:
                    raise serializers.ValidationError(
                        f"Unable to convert data type. Field [{key} : {value}] cannot be converted to {column_type}"
                    )
