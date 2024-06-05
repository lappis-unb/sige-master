import csv
import logging
from io import StringIO
from pathlib import Path

from django.core.files.uploadedfile import InMemoryUploadedFile

logger = logging.getLogger("apps")


def upload_directory_path(instance, filename):
    extension = Path(filename).suffix
    name = instance.name.lower().strip().replace(" ", "_")
    return f"memory_map/{name}{extension}"


def parse_uploaded_csv_file(csv_file: InMemoryUploadedFile) -> list[dict]:
    content = csv_file.read().decode("utf-8").lower().replace(" ", "")
    io_string = StringIO(content)
    reader = csv.DictReader(io_string)
    csv_file.seek(0)

    return [row for row in reader if row.get("active") in ["t", "y", "true", "yes"]]
