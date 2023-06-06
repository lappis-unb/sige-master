from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


def latitude_validator(value):
    if value < -90 or value > 90:
        msg = _(f"{value} is not a valid latitude")
        raise serializers.ValidationError(msg, code="invalid_value")


def longitude_validator(value):
    if value < -180 or value > 180:
        msg = _(f"{value} is not a valid longitude")
        raise serializers.ValidationError(msg, code="invalid_value")
