# (c) 2021, xanthus tan <tanxk@neusoft.com>
import sqlalchemy
from sqlalchemy import select, insert, delete

from src.ump.msg import FAILED
from src.ump.modules.release import UmpReleaseInfo
from src.ump.utils.dbutils import DB
from src.ump.utils.logger import logger


class ReleaseMetaInstance:

    def get_meta_info(self, name, tag):
        db = DB()
        conn = db.get_connect()
        s = select(UmpReleaseInfo).where(UmpReleaseInfo.release_name == name,
                                         UmpReleaseInfo.release_name_tag == tag)
        res = conn.execute(s).fetchone()
        meta_info = {
            "file_id": res._mapping["release_file_id"],
            "app_name": name,
            "app_tag": tag,
            "app_suffix": res._mapping["release_origin_suffix"],
        }
        return meta_info


class ReleaseService:
    def __init__(self):
        db = DB()
        self.conn = db.get_connect()

    def get_release_info(self, release_name):
        if release_name != "":
            s = select(UmpReleaseInfo).where(UmpReleaseInfo.release_name == release_name)
        else:
            s = select(UmpReleaseInfo)
        rs = self.conn.execute(s)
        rows = []
        for r in rs:
            row = {"name": r.release_name,
                   "tag": r.release_name_tag,
                   "file_size(KB)": r.release_file_size,
                   "origin_name": r.release_origin_name,
                   "type": r.release_origin_suffix,
                   "comment": r.release_comment,
                   "push_time": r.release_push_time.strftime("%Y-%m-%d %H:%M:%S")
                   }
            rows.append(row)
        return rows

    def register_app(self, file_id=None,
                     release_name=None,
                     release_tag=None,
                     file_size=None,
                     origin_name=None,
                     origin_suffix=None,
                     comment=None):
        val = [{"release_file_id": file_id,
                "release_name": release_name,
                "release_file_size": file_size,
                "release_origin_name": origin_name,
                "release_origin_suffix": origin_suffix,
                "release_comment": comment,
                "release_name_tag": release_tag}]
        s = insert(UmpReleaseInfo).values(val)
        try:
            self.conn.execute(s)
        except sqlalchemy.exc.IntegrityError as error:
            logger.error(error)
            return FAILED

    def delete_release(self, release_name, release_tag):
        s = delete(UmpReleaseInfo).where(UmpReleaseInfo.release_name == release_name,
                                         UmpReleaseInfo.release_name_tag == release_tag)
        r = self.conn.execute(s)
        return r.rowcount

    def close_db_connection(self):
        self.conn.close()
