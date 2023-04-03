from django.contrib import admin
from . import models

from rest_framework import authtoken
from django_cron.models import CronJobLog
from django.contrib.auth.models import Group

admin.site.unregister(CronJobLog)
admin.site.unregister(authtoken.models.Token)


@admin.register(models.Slave)
class SlaveAdmin(admin.ModelAdmin):
    list_display = (
        'broken',
        'ip_address',
        'port',
        'name',
    )

    list_filter = (
        'broken',
    )
