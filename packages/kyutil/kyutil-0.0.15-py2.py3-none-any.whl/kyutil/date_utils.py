# -*- coding: UTF-8 -*-
import re
import time


def get_today(ts, fmt='%Y-%m-%d'):
    return time.strftime(fmt, time.localtime(ts))


def extract_time_from_line(line, time_pattern):
    match = re.search(time_pattern, line)
    if match:
        return match.group(1)
    return None
