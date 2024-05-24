import logging
import re
from operator import eq, ge, gt, le, lt, ne

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger("apps")


def parse_timedelta(self, period, end_date=timezone.now()):
    if not re.match(r"^\d+[HDWM]$", period, re.IGNORECASE):
        raise ValueError("Invalid period format: {period}. Use 'number + unit' like '30D' for days.")

    number = int(period[:-1])
    unit = period[-1].upper()

    time_delta = {
        "H": end_date - relativedelta(hours=number),
        "D": end_date - relativedelta(days=number),
        "W": end_date - relativedelta(weeks=number),
        "M": end_date - relativedelta(months=number),
    }
    return time_delta[unit]


def get_error_messages(field_type=""):
    MESSAGES = {
        "required": _("Missing required parameter."),
        "invalid_date": _("Date must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."),
    }

    response = {
        "required": MESSAGES["required"],
        "invalid": MESSAGES.get(f"invalid_{field_type}"),
    }
    response = {key: value for key, value in response.items() if value is not None}

    return response


class OperatorFunction:
    operator_functions = {
        "gt": gt,
        "gte": ge,
        "lt": lt,
        "lte": le,
        "exact": eq,
        "ne": ne,
    }

    def __init__(self, operator):
        if operator not in self.operator_functions:
            raise ValueError(f"Unsupported operator: {operator}")
        self.function = self.operator_functions[operator]

    def __call__(self, a, b):
        return self.function(a, b)
