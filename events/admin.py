from django.contrib import admin

from events.models import Event
from events.models import PhaseDropEvent
from events.models import CriticalVoltageEvent
from events.models import PrecariousVoltageEvent
from events.models import FailedConnectionSlaveEvent
from events.models import FailedConnectionTransductorEvent


@admin.register(PhaseDropEvent)
class PhaseDropEventAdmin(admin.ModelAdmin):
    pass


@admin.register(CriticalVoltageEvent)
class CriticalVoltageEventAdmin(admin.ModelAdmin):
    pass


@admin.register(PrecariousVoltageEvent)
class PrecariousVoltageEventAdmin(admin.ModelAdmin):
    pass


@admin.register(FailedConnectionSlaveEvent)
class FailedConnectionSlaveEventAdmin(admin.ModelAdmin):
    pass


@admin.register(FailedConnectionTransductorEvent)
class FailedConnectionTransductorEventAdmin(admin.ModelAdmin):
    pass
