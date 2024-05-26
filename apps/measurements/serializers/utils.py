import re

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


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


def error_msgs(field_type=""):
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


def field_params(field_type):
    FIELD_INFO = {
        "fields": {
            "help_text": "Comma-separated list of fields the model to include in the response.",
        },
        "period": {
            "help_text": "Period to filter the data. Use 'number + unit' like '30D' for days.",
        },
        "date": {
            "help_text": "Must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).",
        },
        "lttb": {
            "help_text": "Enable or disable the LTTB filter.",
            "default": True,
        },
        "threshold": {
            "help_text": "Threshold value to filter LTTB.",
            "default": settings.LIMIT_FILTER,
        },
        "freq": {
            "help_text": "Frequency value to resample the data, like '1H' for hourly.",
        },
        "inc_desc": {
            "help_text": "Include entities descendants in the response.",
            "default": True,
        },
        "entity": {
            "help_text": "Entity ID to filter the data.",
        },
        "transductor": {
            "help_text": "Transductor ID to filter measurements.",
        },
        "agg": {
            "help_text": "Aggregation function to resample the data.",
            "default": "sum",
        },
        "depth": {
            "help_text": "Depth level of the entity hierarchy.",
            "default": 0,
        },
        "only_day": {
            "help_text": "Filter only the data from the same day.",
            "default": True,
        },
        "th_percent": {
            "help_text": "Threshold value to filter the power factor.",
            "default": 0.92,
        },
    }

    msgs = error_msgs(field_type)
    info = FIELD_INFO.get(field_type, {})

    field_details = {
        "error_messages": msgs,
        "help_text": info.get("help_text", f"The {field_type} in a valid format."),
    }

    default_value = info.get("default", "")
    if default_value:
        field_details["default"] = default_value

    return field_details
