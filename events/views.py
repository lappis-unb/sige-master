from django.utils import timezone
import numpy as np
import os

from django.db.models.query import QuerySet

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import mixins

from rest_framework.exceptions import APIException

from .models import *

from .serializers import VoltageRelatedEventSerializer
from .serializers import FailedConnectionSlaveEventSerializer
from .serializers import FailedConnectionTransductorEventSerializer


class EventViewSet(mixins.RetrieveModelMixin,
              mixins.DestroyModelMixin,
              mixins.ListModelMixin,
              viewsets.GenericViewSet):
    queryset = None
    model = None
    fields = []


class VoltageRelatedEventViewSet(EventViewSet):
    pass


class FailedConnectionSlaveEventViewSet(EventViewSet):
    pass


class FailedConnectionTransductorEventViewSet(EventViewSet):
    pass
