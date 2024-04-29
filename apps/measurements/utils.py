import logging
from operator import eq, ge, gt, le, lt, ne

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException

from apps.organizations.models import Organization
from apps.transductors.models import Transductor

logger = logging.getLogger("apps")


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


# ====================================================================================
# TODO: Refactor this class


class MeasurementParamsValidator:
    @staticmethod
    def get_fields():
        return [
            ("id", MeasurementParamsValidator.validate_id),
            ("start_date", MeasurementParamsValidator.validate_start_date),
            ("end_date", MeasurementParamsValidator.validate_end_date),
        ]

    @staticmethod
    def get_ufer_fields():
        return [("date", MeasurementParamsValidator.validate_start_date), ("campus", MeasurementParamsValidator)]

    def validate_query_params(params, ignore=None):
        if ignore is None:
            ignore = []
        fields = MeasurementParamsValidator.get_fields()
        errors = {}
        for field in fields:
            if field[0] not in ignore:
                try:
                    validation_function = field[1]
                    param = params[field[0]]
                    validation_function(param)

                except KeyError:
                    errors[field[0]] = _(f"It must have an {field[0]} argument")
                except ValidationException as e:
                    errors[field[0]] = e

        exception = APIException(
            errors,
            _("This id does not match with any Transductor"),
        )
        exception.status_code = 400
        if errors:
            raise exception

    @staticmethod
    def validate_campus_id(campus_id):
        try:
            Organization.objects.get(id=campus_id)
        except Organization.DoesNotExist:
            raise ValidationException(
                _("This id does not match with any Campus"),
            )

    @staticmethod
    def validate_id(transductor_id):
        try:
            Transductor.objects.get(id=transductor_id)
        except Transductor.DoesNotExist:
            raise ValidationException(_("This id does not match with any Transductor"))

    @staticmethod
    def validate_start_date(start_date):
        try:
            timezone.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            message = "The start_date param must be a valid date in the format YYYY-MM-DD HH:MM:SS"
            raise ValidationException(_(message))

    @staticmethod
    def validate_end_date(end_date):
        try:
            timezone.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            message = "The end_date param must be a valid date in the format YYYY-MM-DD HH:MM:SS"
            raise ValidationException(_(message))
