#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""client log real-time return display module"""
import os
import subprocess
import sys
import time

import cgi

num = 300


def get_last_log_lines_from_pos(pos=1, log_path=None, return_dict=None):
    """ get_last_log_lines_from_pos(pos)"""
    cmd = "tail -n " + str(pos) + " " + str(log_path)
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, encoding="utf-8")
    except TypeError:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    log_file, _ = process.communicate()
    log_content = list(filter(None, log_file.split("\n")))
    return_dict["loglines"] = log_content

    return_dict["count"] = str(len(log_content))
    return_dict["pos"] = str(pos)
    return_dict["cmd"] = cmd


if __name__ == "__main__":
    form = cgi.FieldStorage()
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Method: *")
    print("Access-Control-Allow-Headers: Origin, x-requested-with, content-type, Authorization")
    print("Content-type:text/html\n\n")

    try:
        log_path = form.getvalue("path")
        print(log_path)
    except Exception as err:
        print(err)
        sys.exit(1)

    return_dict = dict()
    return_dict["count"] = ""
    return_dict["loglines"] = []

    if not os.path.exists(str(log_path)):
        for i in range(3):
            log_path_names = log_path.split("/")
            log_path_names[4] = str(str(log_path_names[4]) + str(i))
            log_path_names[6] = str(log_path_names[6].split(".")[0] + str(i) + ".log")
            new_path = "/".join(log_path_names)
            if os.path.exists(new_path):
                log_path = new_path

    if not os.path.exists(str(log_path)):
        return_dict["count"] = "-1"
        return_dict["loglines"] = [log_path + "， 日志文件不存在"]
        # print(json.dumps(return_dict))
        sys.exit(1)

    time.sleep(0.1)  # ?
    get_last_log_lines_from_pos(num, log_path, return_dict)
