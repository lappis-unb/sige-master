import logging

import httpx
from django.core.management import BaseCommand

from slaves.models import Slave
from transductors.models import EnergyTransductor
from utils.helpers import log_execution_time

logger = logging.getLogger("tasks")


class Command(BaseCommand):
    @log_execution_time(logger, level=logging.INFO)
    def handle(self, *args, **options):
        slaves = Slave.objects.filter(active=True)
        logger.info(f"Check Transductors - Active slave servers: {len(slaves)}")

        for slave in slaves:
            url = f"http://{slave.server_address}:{slave.port}/broken-transductors/"

            with httpx.Client() as client:
                try:
                    logger.debug(f"Testing slave server - {slave.server_address}:{slave.port}")
                    response = client.get(url)
                    response.raise_for_status()
                    logger.info(f"Slave server {slave.server_address}:{slave.port} is working")
                    slave.set_broken(False)

                    logger.debug(f"Activating slave server {slave.server_address}:{slave.port}\n")

                    slave_transductors = response.json()["results"]
                    master_transductors = EnergyTransductor.objects.filter(slave_server=slave)

                    self.check_sync_transductors(slave_transductors, master_transductors)
                    self.check_status_transductors(slave_transductors, master_transductors)

                except httpx.HTTPError as exc:
                    slave.set_broken(True)
                    logger.info(f"Slave server {slave.server_address}:{slave.port} is not working")
                    logger.info(f"Deactivate slave server: {slave.server_address}:{slave.port}")
                    logger.execption(f"HTTP Exception for {exc.request.url} - {exc}")
                    raise

    def check_sync_transductors(self, slave_transductors, master_transductors):
        logger.info("Start check sync transductors:")

        slave_ids = {st["id"] for st in slave_transductors}
        master_ids = {mt.id for mt in master_transductors}

        logger.debug(f"Transductors ids in  slave: {slave_ids}")
        logger.debug(f"Transductors ids in master: {master_ids}")

        missing_in_slave = master_ids - slave_ids
        missing_in_master = slave_ids - master_ids

        for master_id in missing_in_slave:
            logger.error(f"Transductor [id={master_id}] not found in slave server")

        for slave_id in missing_in_master:
            logger.error(f"Transductor [id={slave_id}] not found in master server")

        if missing_in_slave or missing_in_master:
            logger.error("Transductors not syncronized!")
            raise Exception("Transductors not syncronized")

        logger.info("Transductors syncronized successfully\n")

    def check_status_transductors(self, slave_transductors, master_transductors):
        logger.info("Start check status transductors:")

        for slave_t in slave_transductors:
            master_t = master_transductors.get(id=slave_t["id"])

            if not master_t:
                logger.error(f"Transductor not found in slave server [ID: {slave_t['id']}]")
                continue

            if master_t.broken != slave_t["broken"]:
                logger.debug(f"Divergent 'broken' status for transductor [ID: {slave_t['id']}]")
                logger.debug(f"Status: (Slave broken: {slave_t['broken']}) (Master broken: {master_t.broken})")
                master_t.broken = slave_t["broken"]
                master_t.save()
                logger.info(f"Updated transductor status master [ID: {slave_t['id']}, Broken: {slave_t['broken']}]\n")

            else:
                logger.debug(
                    f"Transductor same status in slave and master [ID: {slave_t['id']}, Broken: {slave_t['broken']}]"
                )
