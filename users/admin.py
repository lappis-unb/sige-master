from rest_framework import authtoken
from django_cron.models import CronJobLog
from django.contrib.auth.models import Group


admin.site.unregister(CronJobLog)
admin.site.unregister(authtoken.models.Token)
