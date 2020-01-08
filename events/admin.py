from django.contrib import admin

from events.models import Event
from events.models import PhaseDropEvent
from events.models import CriticalVoltageEvent
from events.models import PrecariousVoltageEvent
from events.models import FailedConnectionSlaveEvent
from events.models import FailedConnectionTransductorEvent


admin.site.register(PhaseDropEvent)
admin.site.register(CriticalVoltageEvent)
admin.site.register(PrecariousVoltageEvent)
admin.site.register(FailedConnectionSlaveEvent)
admin.site.register(FailedConnectionTransductorEvent)
