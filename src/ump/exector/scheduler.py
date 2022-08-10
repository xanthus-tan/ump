# (c) 2021, xanthus tan <tanxk@neusoft.com>
from abc import ABC, abstractmethod
from sqlite3 import OperationalError

import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import Column, Integer, Sequence, String, DateTime, UniqueConstraint, insert, delete, select
from sqlalchemy.orm import declarative_base
from src.ump.utils.logger import logger
from src.ump.utils import get_current_local_datetime
from src.ump.utils.dbutils import DB
from src.ump.utils import get_unique_id
from src.ump.modules import module_names
scheduler = BackgroundScheduler()
STOP = "stop"
START = "start"


def job_startup():
    jds = JobDBService()
    types = jds.get_job_type()
    if len(types) == 0:
        logger.info("Not found running job")
        return
    for job_type in types:
        if job_type not in module_names:
            logger.error("not found module" + job_type)
            continue
        try:
            module_class = "Action"
            my_handler = getattr(__import__("src.ump.modules.{0}".format(job_type), fromlist=[module_class]), module_class)
            module = my_handler()
            jobs = jds.get_started_jobs_by_type(job_type)
            jds.close_job_db_connection()
            module.job_boot(jobs)
        except ModuleNotFoundError as error:
            logger.error("job boot error: module error")
            logger.error(error)
            jds.close_job_db_connection()
    jds.close_job_db_connection()


class UmpJob(ABC):
    @abstractmethod
    def job_boot(self, **args):
        pass


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
        scheduler.add_job(self.func, 'interval',
                          args=self.func_args,
                          seconds=self.seconds,
                          id=self.job_id,
                          max_instances=50)
        if scheduler.state == 0:
            scheduler.start()

    def job_stop(self, job_id):
        try:
            scheduler.remove_job(job_id=job_id)
        except apscheduler.jobstores.base.JobLookupError:
            logger.error("not found " + job_id + " in job")
        scheduler.print_jobs()


class JobDBService:
    def __init__(self):
        db = DB()
        self.conn = db.get_connect()
        self.job_id = ""
        self.job_interval = None

    def save_job(self, target_name, target_type, interval, ssh_timeout):
        self.job_id = get_unique_id()
        self.job_interval = interval
        val = {
            "job_id": self.job_id,
            "job_target_name": target_name,
            "job_type": target_type,
            "job_interval": interval,
            "job_status": START,
            "job_start_time": get_current_local_datetime(),
            "job_ssh_timeout": ssh_timeout
        }
        s = insert(JobModel).values(val)
        self.conn.execute(s)
        return self.job_id

    def job_begin(self, callback, args):
        job = Job()
        job.set_job_id(self.job_id)
        job.set_job_interval(self.job_interval)
        job.set_job_func(callback, args)
        job.job_start()

    def get_job_id_by_target(self, target_name, target_type):
        s = select(JobModel).where(JobModel.job_target_name == target_name,
                                   JobModel.job_type == target_type)
        rs = self.conn.execute(s).fetchone()
        if rs is None:
            return None
        job_id = rs["job_id"]
        return job_id

    def get_started_jobs_by_type(self, job_type):
        s = select(JobModel).where(JobModel.job_type == job_type, JobModel.job_status == START)
        jobs = []
        rs = self.conn.execute(s)
        for r in rs:
            jobs.append({
                "job_id": r["job_id"],
                "job_target_name": r["job_target_name"],
                "job_interval": r["job_interval"],
                "job_ssh_timeout": r["job_ssh_timeout"]
            })
        return jobs

    def delete_job_by_target(self, target_name, target_type):
        job_id = self.get_job_id_by_target(target_name, target_type)
        if job_id is None:
            return None
        job = Job()
        job.job_stop(job_id)
        s = delete(JobModel).where(JobModel.job_target_name == target_name,
                                   JobModel.job_type == target_type)
        self.conn.execute(s)

    def get_job_type(self):
        s = select(JobModel.job_type).where(JobModel.job_status == START).group_by(JobModel.job_type)
        rs = self.conn.execute(s)
        types = []
        for r in rs:
            job_type = r["job_type"]
            types.append(job_type)
        return types

    def delete_job_by_job_id(self, job_id):
        pass

    def update_job_status(self, status):
        pass

    def close_job_db_connection(self):
        self.conn.close()


Base = declarative_base()


# 主机数据模型
class JobModel(Base):
    __tablename__ = "ump_job_info"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    job_id = Column(String(40))
    job_target_name = Column(String(20))
    job_interval = Column(Integer)
    job_type = Column(String(20))
    job_status = Column(String(10), default=STOP)
    job_create_time = Column(DateTime, default=get_current_local_datetime)
    job_start_time = Column(DateTime)
    job_reason = Column(String(50))
    job_ssh_timeout = Column(String(10))
    __table_args__ = (
        UniqueConstraint("job_id"),
        UniqueConstraint("job_target_name", "job_type"),  # job目标和job类型不能重复
    )


db = DB()
engine = db.get_db_engine()
Base.metadata.create_all(engine)
