import logging

from django.utils import timezone

from apps.events.models import Event
from apps.transductors.models import StatusHistory
from apps.utils.helpers import log_service

logger = logging.getLogger("apps")


class MeasurementEventManager:
    def __init__(self, measurement, field_name):
        self.measurement = measurement
        self.transductor = measurement.transductor
        self.field_name = field_name
        self.field_value = getattr(measurement, field_name)

    @log_service()
    def perform_triggers(self, triggers):
        self.log_start()

        if self.field_value is None:
            logger.error(f"No value for field '{self.field_name}' - skipping triggers")
            return

        if not triggers.exists():
            logger.error(f"No active triggers found for {self.measurement.__class__.__name__}")
            return

        current_event = self.get_current_event(triggers)
        if current_event:
            self.process_current_event(current_event, triggers)
        else:
            self.check_and_create_event(triggers)

    def process_current_event(self, event, triggers):
        logger.info(f"Processing existing event: {event.id}")
        trigger = triggers.filter(id=event.trigger.id).first()

        if self.is_within_threshold(trigger):
            logger.info(f"No action taken: Event {event.id} conditions continue to be met.")
        else:
            self.close_event(event)
            self.check_and_create_event(triggers)

    def check_and_create_event(self, triggers):
        logger.info("Checking and creating event...")
        for trigger in triggers:
            logger.info(f"Checking trigger: {trigger.id}")
            if self.is_within_threshold(trigger):
                self.create_event(trigger)
                break
            else:
                logger.info("Trigger condition not met!")

    def is_within_threshold(self, trigger):
        if self.measurement.__class__.__name__ == "CumulativeMeasurement":
            base_value = trigger.calculate_metric(self.transductor, self.measurement.collection_date)
            upper_threshold = trigger.calculate_threshold(base_value, trigger.upper_threshold_percent)
            lower_threshold = trigger.calculate_threshold(base_value, trigger.lower_threshold_percent)
        elif self.measurement.__class__.__name__ == "InstantMeasurement":
            lower_threshold = trigger.lower_threshold if trigger.lower_threshold is not None else float("-inf")
            upper_threshold = trigger.upper_threshold if trigger.upper_threshold is not None else float("inf")

        is_within = lower_threshold <= self.field_value < upper_threshold
        logger.info(f"Conditions: {lower_threshold:.3f} <= {self.field_value} < {upper_threshold:.3f} = {is_within}")
        return is_within

    def create_event(self, trigger):
        new_event = Event.objects.create(
            trigger=trigger,
            transductor=self.transductor,
            is_active=True,
        )
        logger.info(f"New event created: {new_event.id}, for trigger: {trigger.id},  field: {self.field_name}.")
        return new_event

    def close_event(self, event):
        event.close_event()
        logger.info(f"Event {event.id} closed: conditions no longer met!")

    def get_current_event(self, triggers):
        events = Event.objects.filter(
            trigger__in=triggers,
            transductor=self.transductor,
            is_active=True,
        )

        if events.count() > 1:
            error_msg = f"Abort: More than one active event found: {self.transductor} - {self.field_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        return events.first()

    def log_start(self):
        logger.info("-" * 65)
        logger.info(f"=> Starting Perform triggers {self.measurement.__class__.__name__}")
        logger.debug(f"   Transductor: {self.transductor}")
        logger.debug(f"   Field name:  {self.field_name}")
        logger.debug(f"   Field value: {self.field_value}")
        logger.info("-" * 65)


# TODO - Refatorar para simplificar e evitar duplicações com MeasurementEventManager:
# - Implementar uma classe base comum.
# - Refinar a lógica de criação de eventos.
# - Limpar logs de debug desnecessários.
class TransductorEventManager:
    def perform_close_status(self, status):
        status.close_status()
        logger.info(f"Status {status.id} closed: conditions no longer met!")

    @log_service()
    def perform_triggers(self, triggers):
        proc_status_ids = set()

        for trigger in triggers:
            logger.info(f"Processing trigger: {trigger.id}")
            self.log_triggers(trigger)
            broken_status_history = self.get_broken_status_history(trigger, proc_status_ids)

            for status in broken_status_history:
                self.log_status_history(status)
                if self.has_active_event(status, trigger):
                    logger.info(f"Event already exists for {status.transductor} - skipping\n")
                else:
                    self.close_other_events(status, triggers)
                    self.create_event(trigger, status)
                proc_status_ids.add(status.id)

    def get_broken_status_history(self, trigger, proc_status_ids):
        current_time = timezone.now()

        broken_status_history = StatusHistory.objects.filter(
            status=trigger.target_status,
            start_time__lte=current_time - trigger.threshold_time,
            end_time__isnull=True,
        ).exclude(id__in=proc_status_ids)

        logger.info(f"Broken status history meet the trigger: {broken_status_history.count()}")
        return broken_status_history

    def has_active_event(self, status, trigger):
        return Event.objects.filter(
            transductor=status.transductor,
            trigger=trigger,
            is_active=True,
        ).exists()

    def create_event(self, trigger, status):
        new_event = Event.objects.create(
            trigger=trigger,
            transductor=status.transductor,
            is_active=True,
        )
        logger.info(f"New event created: {new_event.id} for trigger: {trigger.id}.")

    def close_other_events(self, status, triggers):
        for trigger in triggers:
            event = Event.objects.filter(
                transductor=status.transductor,
                trigger=trigger,
                is_active=True,
            ).first()

            if event:
                self.close_event(event)

    def close_event(self, event):
        event.close_event()
        logger.info(f"Event {event.id} closed: conditions no longer met!")

    def log_triggers(self, trigger):
        logger.info("_" * 70)
        logger.info(f"Trigger ID: {trigger.id}")
        logger.info(f"Trigger Name: {trigger.name}")
        logger.info(f"Target Status: {trigger.get_target_status_display()}")
        logger.info(f"Category: {trigger.get_category_display()}")
        logger.info(f"Severity: {trigger.get_severity_display()}")
        logger.info(f"Threshold Time: {trigger.threshold_time}")
        logger.info("_" * 70)

    def log_status_history(self, status):
        logger.info("_" * 70)
        logger.info(f"Transductor: {status.transductor}")
        logger.info(f"Status: {status.get_status_display()}")
        logger.info(f"Start Time: {status.start_time}")
        logger.info(f"End Time: {status.end_time}")
        logger.info(f"Duration: {status.duration}")
        logger.info(f"Elapsed Time: {timezone.now() - status.start_time}")
        logger.info("_" * 70)
