# (c) 2021, xanthus tan <tanxk@neusoft.com>

from sqlalchemy import Column, Integer, String, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base

from src.ump.utils import get_current_local_datetime
from src.ump.utils.dbutils import DB

Base = declarative_base()


# deploy数据模型
class UmpDeployInfo(Base):
    __tablename__ = "ump_deploy_info"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    deploy_name = Column(String(50))
    deploy_path = Column(String(50))
    deploy_app = Column(String(40))
    deploy_app_last = Column(String(40))
    deploy_group = Column(String(20))
    deploy_host_num = Column(Integer)
    deploy_failed_num = Column(Integer)
    deploy_comment = Column(String(100))
    deploy_status = Column(String(20), default="current")
    deploy_time = Column(DateTime, default=get_current_local_datetime())
    # __table_args__ = (
    #     UniqueConstraint('deploy_name'),  # 部署名称不会重复
    # )


class UmpDeployDetailInfo(Base):
    __tablename__ = "ump_deploy_detail_info"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    deploy_name = Column(String(50))
    deploy_host = Column(String(30))
    deploy_status = Column(String(20))
    deploy_time = Column(DateTime, default=get_current_local_datetime())


db = DB()
engine = db.get_db_engine()
Base.metadata.create_all(engine)