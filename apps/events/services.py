import logging

from apps.events.models import Event
from apps.utils.helpers import log_service

logger = logging.getLogger("apps")


class TriggerService:
    def __init__(self, trigger, current_measurement):
        self.trigger = trigger
        self.measurement = current_measurement
        self.field_name = trigger.field_name
        self.field_value = getattr(current_measurement, trigger.field_name)

    @log_service()
    def perform_trigger(self):
        self.log_start()

        if self.field_value is None:
            self.insert_log("Abort: Collected value is None. Trigger processing halted", level=logging.WARNING)
            return None

        event = Event.objects.filter(
            measurement_trigger=self.trigger,
            transductor=self.measurement.transductor,
            is_active=True,
        ).first()

        if event.exists():
            self.insert_log("Found existing event:")
            self.process_existing_event(event)
        else:
            self.insert_log("No active event found, creating new event.")
            self.process_no_existing_event()

    def process_existing_event(self, event):
        self.insert_log(f"Processing existing event: {event.id}")
        threshold = self.trigger.deactivate_threshold or self.trigger.active_threshold

        if self.meets_trigger_condition(threshold):
            self.insert_log("No action taken: event remains active as conditions are not met.")
        else:
            event.close_event()
            self.insert_log(f"Event {event} closed: condition met.")

    def process_no_existing_event(self):
        if self.meets_trigger_condition(self.trigger.active_threshold):
            new_event = Event.objects.create(
                measurement_trigger=self.trigger,
                transductor=self.measurement.transductor,
                event_type=self.trigger.event_type,
                is_active=True,
            )
            self.insert_log(f"New event created: {new_event}, condition met.")
        else:
            self.insert_log("Condition not met: no new event created.")

    def meets_trigger_condition(self, threshold):
        operator_functions = {
            "gt": lambda x, y: x > y,
            "gte": lambda x, y: x >= y,
            "lt": lambda x, y: x < y,
            "lte": lambda x, y: x <= y,
            "exact": lambda x, y: x == y,
            "ne": lambda x, y: x != y,
        }

        if self.trigger.operator not in operator_functions:
            self.insert_log(f"Error: Invalid operator '{self.trigger.operator}' used.", level=logging.ERROR)
            raise ValueError("Invalid operator")

        result = operator_functions[self.trigger.operator](self.field_value, threshold)
        self.insert_log(
            f"Condition check: {self.field_value} {self.trigger.operator} {threshold} = {result}",
            level=logging.DEBUG,
        )
        return result

    def log_start(self):
        logger.info("-" * 85)
        logger.info(f"=> Starting Perform trigger {self.trigger.id} - {self.measurement.__class__.__name__}")
        logger.debug(f"   Transductor: {self.measurement.transductor}")
        logger.debug(f"   Measurement: {self.measurement.id}")
        logger.debug(f"   Field name:  {self.field_name}")
        logger.debug(f"   Field value: {self.field_value}")
        logger.info("-" * 85)

    def add_log(self, message, level=logging.INFO, raise_exception=False):
        logger.log(level, f"Trigger {self.trigger.id}: {message}")

        if raise_exception:
            raise ValueError(message)
