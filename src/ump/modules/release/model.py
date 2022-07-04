# (c) 2021, xanthus tan <tanxk@neusoft.com>

from sqlalchemy import Column, Integer, String, DateTime, Sequence, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

from src.ump.utils import get_current_local_datetime
from src.ump.utils.dbutils import DB

Base = declarative_base()


# release数据模型
class UmpReleaseInfo(Base):
    __tablename__ = "ump_release_info"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    release_file_id = Column(String(50))
    release_name = Column(String(30))
    release_name_tag = Column(String(30))
    release_file_size = Column(Integer())
    release_origin_name = Column(String(50))
    release_origin_suffix = Column(String(10))
    release_comment = Column(String(100))
    release_push_time = Column(DateTime, default=get_current_local_datetime)
    __table_args__ = (
        UniqueConstraint('release_name', 'release_name_tag'),  # 发布的项目name:tag不能重复
    )


db = DB()
engine = db.get_db_engine()
Base.metadata.create_all(engine)
