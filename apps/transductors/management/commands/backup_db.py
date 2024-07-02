import logging
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone

from apps.utils.helpers import log_execution_time

logger = logging.getLogger("tasks")


class Command(BaseCommand):
    help = "Backup the database."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--max_backups", type=int, default=7)

    @log_execution_time(logger, level=logging.INFO)
    def handle(self, *args, **options) -> None:
        logger.info("   Backup database - Starting...")

        db_config = settings.DATABASES["default"]
        db_host = db_config["HOST"]
        db_port = db_config["PORT"]
        db_name = db_config["NAME"]
        db_user = db_config["USER"]

        max_backups = options["max_backups"]
        backup_path = settings.BASE_DIR / "backups"
        backup_path.mkdir(parents=True, exist_ok=True)

        timestamp = timezone.localtime(timezone.now()).strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = backup_path / f"bkp_{db_name}_{timestamp}.dump.gz"

        logger.info(f"Backup path: {backup_file}")
        command = f"pg_dump -h {db_host} -p {db_port} -U {db_user} {db_name} | gzip > {backup_file}"

        self.backup_db(command, db_config, backup_path, max_backups)

    def backup_db(self, command, db_config, backup_path, max_backups) -> None:
        try:
            logger.info("Running backup command...")
            subprocess.run(command, shell=True, check=True, env={"PGPASSWORD": db_config["PASSWORD"]})
            logger.debug("-" * 85)
            logger.info("Backup completed successfully.")
            self.clean_backups(backup_path, max_backups)
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {e}")

    def clean_backups(self, backup_path, max_backups) -> None:
        logger.info("Verifying number of backups...")
        backups = sorted(backup_path.glob("*.dump.gz"), reverse=True)
        for backup in backups[max_backups:]:
            logger.info(f"Removing old backup: {backup}")
            backup.unlink()
