from django_cron import CronJobBase, Schedule
from datetime import datetime
from .utils import CheckTransductorsAndSlaves


class CheckTransductorBrokenCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'slaves.cronjob.CheckTransductorBroken'

    def do(self):
        now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        checker = CheckTransductorsAndSlaves()
        checker.check_transductors()
        print("Checking transductors at {}".format(now))


class GetAllMeasurementsCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'slaves.cronjob.GetAllMeasurements'

    def do(self):
        print("Get all measurements.")
