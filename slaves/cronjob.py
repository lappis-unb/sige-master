from django_cron import CronJobBase, Schedule

class CheckTransductorBrokenCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'slaves.cronjob.CheckTransductorBroken'

    def do(self):
        print("Check all broken transductors.")

class GetAllMeasurementsCronJob(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'slaves.cronjob.GetAllMeasurements'

    def do(self):
        print("Get all measurements.")
