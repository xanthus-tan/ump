# (c) 2021, xanthus tan <tanxk@neusoft.com>
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import Column, Integer, Sequence, String, DateTime, UniqueConstraint, insert, delete, select
from sqlalchemy.orm import declarative_base
from src.ump.utils.logger import logger
from src.ump.utils import get_current_local_datetime
from src.ump.utils.dbutils import DB
from src.ump.utils import get_unique_id

scheduler = BackgroundScheduler()
STOP = "stop"
START = "start"
DEFAULT_HEALTH_INTERVAL = 10


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

    def save_job(self, target_id, target_type):
        job_id = get_unique_id()
        val = {
            "job_id": job_id,
            "job_target_id": target_id,
            "job_type": target_type,
            "job_interval": DEFAULT_HEALTH_INTERVAL,
            "job_status": STOP
        }
        s = insert(JobModel).values(val)
        self.conn.execute(s)
        return job_id

    def get_job_id_by_target(self, target_id, target_type):
        s = select(JobModel).where(JobModel.job_target_id == target_id,
                                   JobModel.job_type == target_type)
        rs = self.conn.execute(s).fetchone()
        job_id = rs["job_id"]
        return job_id

    def delete_job_by_target(self, target_id, target_type):
        s = delete(JobModel).where(JobModel.job_target_id == target_id,
                                   JobModel.job_type == target_type)
        self.conn.execute(s)

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
    job_target_id = Column(Integer)
    job_interval = Column(Integer)
    job_type = Column(String(20))
    job_status = Column(String(10), default=STOP)
    job_create_time = Column(DateTime, default=get_current_local_datetime)
    job_start_time = Column(DateTime)
    job_reason = Column(String(50))
    __table_args__ = (
        UniqueConstraint("job_id"),
        UniqueConstraint("job_target_id", "job_type"),  # 主机和组的组合不能重复
    )


db = DB()
engine = db.get_db_engine()
Base.metadata.create_all(engine)
