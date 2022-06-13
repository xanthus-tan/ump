# (c) 2021, xanthus tan <tanxk@neusoft.com>

import os
import re
import shutil


# src file move to new path
def mv_file(src, des):
    if not os.path.exists(src):
        return 1
    shutil.move(src, des)


def is_windows_drive_letter(prefix):
    letter_reg = "^[A-Za-z]:"
    is_letter = re.match(letter_reg, prefix)
    return is_letter


def is_linux_drive_letter(prefix):
    return "/" == prefix
