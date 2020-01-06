from django.contrib import admin

from events.models import Event
from events.models import PhaseDropEvent
from events.models import VoltageRelatedEvent
from events.models import FailedConnectionSlaveEvent
from events.models import FailedConnectionTransductorEvent


admin.site.register(PhaseDropEvent)
admin.site.register(VoltageRelatedEvent)
admin.site.register(FailedConnectionSlaveEvent)
admin.site.register(FailedConnectionTransductorEvent)
