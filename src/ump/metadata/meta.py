# (c) 2021, xanthus tan <tanxk@neusoft.com>
from src.ump.modules.release.meta import ReleaseMetaInstance


class ReleaseMeta:
    def __init__(self, name, tag):
        meta = ReleaseMetaInstance()
        self.info = meta.get_meta_info(name, tag)

    def get_file_id(self):
        return self.info["file_id"]

    def get_file_suffix(self):
        return self.info["app_suffix"]
