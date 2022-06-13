# (c) 2021, xanthus tan <tanxk@neusoft.com>
from sqlalchemy import select

from modules.release import UmpReleaseInfo
from utils.dbutils import DB


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


