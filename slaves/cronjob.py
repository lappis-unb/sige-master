from django_cron import CronJobBase, Schedule
from datetime import datetime
from .utils import CheckTransductorsAndSlaves
from .utils import DataCollector
from django.utils.translation import gettext_lazy as _


class CheckTransductorBrokenCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'slaves.cronjob.CheckTransductorBroken'

    class Meta:
        verbose_name = _('Check meters cronjob')

    def do(self):
        now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        checker = CheckTransductorsAndSlaves()
        checker.check_transductors()
        print("Checking transductors at {}".format(now))


class GetAllMeasurementsCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'slaves.cronjob.GetAllMeasurements'

    class Meta:
        verbose_name = _('Get all measurements cronjob')

    def do(self):
        now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        collector = DataCollector()
        collector.get_measurements(minutely=True, quarterly=True, monthly=True)
        print("Collecting measurements at {}".format(now))


class GetAllEventsCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'slaves.cronjob.GetAllEvents'

    def do(self):
        now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        collector = DataCollector()
        collector.get_events()
        print("Getting events at {}".format(now))


class GetRealTimeMeasurementsCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'slaves.cronjob.GetRealTimeMeasurements'

    class Meta:
        verbose_name = _('Get real time measurements cronjob')

    def do(self):
        now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        collector = DataCollector()
        collector.get_measurements(realtime=True)
        print("Collecting real time measurements at {}".format(now))
