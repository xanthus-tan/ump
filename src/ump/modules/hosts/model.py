# (c) 2021, xanthus tan <tanxk@neusoft.com>

from sqlalchemy import Column, Integer, String, DateTime, Sequence, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

from src.ump.utils import get_current_local_datetime
from src.ump.utils.dbutils import DB

Base = declarative_base()

HOST_ONLINE = "1"
HOSE_DOWN = "2"


# 主机数据模型
class UmpHostsInfo(Base):
    __tablename__ = "ump_hosts_info"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    address = Column(String(30))
    port = Column(Integer)
    group_id = Column(String(20))
    status = Column(String(10), default=HOST_ONLINE)
    register_time = Column(DateTime, default=get_current_local_datetime)
    login_username = Column(String(40))
    login_password = Column(String(40))
    __table_args__ = (
        UniqueConstraint('address', 'group_id'),  # 主机和组的组合不能重复
    )


db = DB()
engine = db.get_db_engine()
Base.metadata.create_all(engine)
