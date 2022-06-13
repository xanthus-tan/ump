# (c) 2021, xanthus tan <tanxk@neusoft.com>

import json

from . import Translate


class CLITranslate(Translate):

    def __init__(self):
        pass

    def to_json(self, cmd):
        f = cmd.replace("\'", "\"").replace("None", "\"\"")
        return json.loads(f)

