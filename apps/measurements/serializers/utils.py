import re

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample


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
        },
        "depth": {
            "help_text": "Depth level of the entity hierarchy.",
            "default": 0,
        },
        "only_day": {
            "help_text": "Filter only data that occurred during the day period (solar time).",
            "default": False,
        },
        "th_percent": {
            "help_text": "Threshold value to filter the power factor.",
            "default": 92,
        },
        "detail_profile": {
            "help_text": "Return the detailed profile average per quarter-hour of the period.",
            "default": False,
        },
        "peak_hours": {
            "help_text": "Filter only data that occurred during the peak hours (18:00 - 20:59 UTC-3).",
            "default": False,
        },
        "off_peak_hours": {
            "help_text": "Filter data that occurred outside the peak hours (21:00 - 23:59 UTC-3).",
            "default": False,
        },
        "detail_report": {
            "help_text": "Return the detailed report with the aggregation per transductor.",
            "default": False,
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


# ==========================================================================================================
# Examples for OpenAPI documentation
# ==========================================================================================================

_graph_data_example = {
    "information": {
        "time_zone": "America/Sao_Paulo (UTC-03)",
        "date_format": "ISO-8601",
        "start_date": "2024-05-15T17:15:41.602645-03:00",
        "end_date": "2024-05-16T14:15:39.424825-03:00",
        "count": 3,
        "fields": ["active_generated", "active_consumption"],
    },
    "timestamp": [
        "2024-05-16T15:15:39.534610-03:00",
        "2024-05-16T15:00:39.534610-03:00",
        "2024-05-16T14:30:39.398148-03:00",
    ],
    "traces": [
        {
            "field": "active_generated",
            "avg_value": 1.88,
            "max_value": 7.72,
            "min_value": 0.0,
            "values": [
                7.72,
                4.32,
                0.14,
            ],
        },
        {
            "field": "active_consumption",
            "avg_value": 0.0,
            "max_value": 0.01,
            "min_value": 0.0,
            "values": [
                0.01,
                0.01,
                0.0,
            ],
        },
    ],
}


_daily_profile_hourly = [
    {
        "time": "00:00:00",
        "active_generated": 0.0,
        "active_consumption": 0.0,
        "reactive_inductive": 0.0,
        "reactive_capacitive": 0.01,
    },
    {
        "time": "04:00:00",
        "active_generated": 0.0,
        "active_consumption": 0.0,
        "reactive_inductive": 0.0,
        "reactive_capacitive": 0.01,
    },
    {
        "time": "08:00:00",
        "active_generated": 0.05,
        "active_consumption": 0.0,
        "reactive_inductive": 0.0,
        "reactive_capacitive": 0.16,
    },
    {
        "time": "12:00:00",
        "active_generated": 15.95,
        "active_consumption": 0.0,
        "reactive_inductive": 0.86,
        "reactive_capacitive": 0.66,
    },
    {
        "time": "16:00:00",
        "active_generated": 17.99,
        "active_consumption": 0.0,
        "reactive_inductive": 1.13,
        "reactive_capacitive": 0.49,
    },
    {
        "time": "20:00:00",
        "active_generated": 1.22,
        "active_consumption": 0.0,
        "reactive_inductive": 0.0,
        "reactive_capacitive": 1.22,
    },
    {
        "time": "23:00:00",
        "active_generated": 0.0,
        "active_consumption": 0.0,
        "reactive_inductive": 0.0,
        "reactive_capacitive": 0.02,
    },
]


_ufer_report_example = {
    "Entity": "FGA - Faculdade do Gama",
    "total_measurements": 21059,
    "info": "Results in (%) above the threshold 92%.",
    "results": [
        {
            "located": "UAC - Unidade Acadêmica",
            "ip_address": "164.41.20.230",
            "total_measurements": 2339,
            "transductor": 1,
            "pf_phase_a": 73.72,
            "pf_phase_b": 68.34,
            "pf_phase_c": 70.08,
        },
        {
            "located": "UAC - Unidade Acadêmica",
            "ip_address": "164.41.20.231",
            "total_measurements": 2340,
            "transductor": 2,
            "pf_phase_a": 74.92,
            "pf_phase_b": 70.72,
            "pf_phase_c": 71.74,
        },
        {
            "located": "UED - Unidade de Ensino e Docência",
            "ip_address": "164.41.20.233",
            "total_measurements": 2340,
            "transductor": 3,
            "pf_phase_a": 81.08,
            "pf_phase_b": 81.08,
            "pf_phase_c": 66.92,
        },
    ],
}

_energy_report_example = {
    "Entity": "FGA - Faculdade do Gama",
    "total_measurements": 14466,
    "tariff_peak": 1.4300,
    "tariff_off_peak": 0.6954,
    "results": {
        "active_consumption_peak": 0.88,
        "active_consumption_off_peak": 11207.37,
        "active_generated_peak": 0.56,
        "active_generated_off_peak": 15516.24,
    },
    "info": "Results in kWh",
}

energy_report_example = OpenApiExample(
    name="Standard Example",
    value=_energy_report_example,
    response_only=True,
    request_only=False,
    description="Example of a response with energy report data.",
)

ufer_report_example = OpenApiExample(
    name="Standard Example",
    value=_ufer_report_example,
    response_only=True,
    request_only=False,
    description="Example of a response with Ufer report data.",
)

daily_profile_hourly_example = OpenApiExample(
    name="Name deve ser alterado",
    value=_daily_profile_hourly,
    response_only=True,
    request_only=False,
    description="Example of a response with daily profile hourly data.",
)

graph_data_example = OpenApiExample(
    name="Standard Example",
    value=_graph_data_example,
    response_only=True,
    request_only=False,
    description="Example of a response with graph data.",
)
