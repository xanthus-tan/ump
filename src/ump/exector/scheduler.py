# (c) 2021, xanthus tan <tanxk@neusoft.com>
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from src.ump.utils.logger import logger

scheduler = BackgroundScheduler()


class Job:
    def __init__(self):
        self.seconds = None
        self.func = None
        self.func_args = None
        self.job_id = None

    def set_job_interval(self, seconds):
        self.seconds = seconds

    def set_job_func(self, func, args=None):
        self.func = func
        self.func_args = args

    def set_job_id(self, job_id):
        self.job_id = job_id

    def job_start(self):
        scheduler.add_job(self.func, 'interval', args=self.func_args, seconds=self.seconds, id=self.job_id)
        if scheduler.state == 0:
            scheduler.start()

    def job_stop(self, job_id):
        s = scheduler.state
        try:
            scheduler.remove_job(job_id=job_id)
        except apscheduler.jobstores.base.JobLookupError:
            logger.error("not found " + job_id + " in job")
        scheduler.print_jobs()


