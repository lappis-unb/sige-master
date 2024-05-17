import logging
from operator import eq, ge, gt, le, lt, ne

from django.utils.translation import gettext_lazy as _

logger = logging.getLogger("apps")


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
