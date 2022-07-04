# (c) 2021, xanthus tan <tanxk@neusoft.com>

from sqlalchemy import Column, Integer, String, DateTime, Sequence, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

from src.ump.utils import get_current_local_datetime
from src.ump.utils.dbutils import DB

Base = declarative_base()


# deploy数据模型
class UmpInstanceInfo(Base):
    __tablename__ = "ump_instance_info"
    id = Column(Integer, Sequence('instance_id_seq'), primary_key=True)
    instance_id = Column(String(50))
    instance_path = Column(String(50))
    instance_pid = Column(String(10))
    instance_port = Column(String(10))
    instance_group = Column(String(40))
    instance_host = Column(String(20))
    instance_deploy_name = Column(String(20))
    instance_status = Column(String(20), default="current")
    instance_start_time = Column(DateTime)
    instance_stop_time = Column(DateTime, default=get_current_local_datetime)
    __table_args__ = (
        UniqueConstraint('instance_id'),  # 实例名称不会重复
    )


db = DB()
engine = db.get_db_engine()
Base.metadata.create_all(engine)