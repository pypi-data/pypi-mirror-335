# -*- coding: UTF-8 -*-
import os
import time

from kobo.shortcuts import force_list
from productmd.composeinfo import ComposeInfo

from .base import get_today


def del_note(s):
    return s.split("#")[0].strip().strip('"').strip("'")


def get_pattern(config_filepath) -> str:
    release_short, release_version, release_type_suffix = "", "", ""
    if not os.path.isfile(config_filepath):
        return "no_config_file"

    for i in open(config_filepath, "r"):
        if i.strip() and i.find("release_short") >= 0 and not release_short:
            release_short = del_note(i.split("=")[-1].strip() or "")
        elif i.strip() and i.find("release_version") >= 0 and not release_version:
            release_version = del_note(i.split("=")[-1].strip() or "")
        elif i.strip() and i.find("release_type_suffix") >= 0 and not release_type_suffix:
            release_type_suffix = del_note(i.split("=")[-1].strip() or "")
    return "%s-%s%s" % (release_short, release_version, release_type_suffix)


def del_note(s):
    return s.split("#")[0].strip().strip('"').strip("'")


def get_pattern(config_filepath) -> str:
    release_short, release_version, release_type_suffix = "", "", ""
    if not os.path.isfile(config_filepath):
        return ""

    for i in open(config_filepath, "r"):
        if i.strip() and i.find("release_short") >= 0 and not release_short:
            release_short = del_note(i.split("=")[-1].strip() or "")
        elif i.strip() and i.find("release_version") >= 0 and not release_version:
            release_version = del_note(i.split("=")[-1].strip() or "")
        elif i.strip() and i.find("release_type_suffix") >= 0 and not release_type_suffix:
            release_type_suffix = del_note(i.split("=")[-1].strip() or "")
    return "%s-%s%s" % (release_short, release_version, release_type_suffix)


def get_work_dir(task_id, config_filepath, root_path_build="/mnt/iso_builder/isobuild/", product_code="") -> str:
    """
    通过配置获取工作目录
    Args:
        task_id:
        config_filepath:
        root_path_build:
        product_code: 产品代号,类似V11

    Returns:

    """
    pattern = get_pattern(config_filepath)
    if not pattern:
        return ""
    work_dir = root_path_build + os.sep + product_code + os.sep + pattern + "-" + get_today(ts=time.time(), fmt="%Y%m%d%H%M") + "-" + task_id[:4] + os.sep
    return work_dir.replace("//", "/")


def get_compose_info(
        conf,
        compose_type="production",
        compose_date=None,
        compose_respin=None,
        compose_label=None,
):
    """
       Creates inncomplete ComposeInfo to generate Compose ID
    """
    ci = ComposeInfo()
    ci.release.name = conf["release_name"]
    ci.release.short = conf["release_short"]
    ci.release.version = conf["release_version"]
    ci.release.is_layered = True if conf.get("base_product_name", "") else False
    ci.release.type = conf.get("release_type", "ga").lower()
    ci.release.internal = bool(conf.get("release_internal", False))
    if ci.release.is_layered:
        ci.base_product.name = conf["base_product_name"]
        ci.base_product.short = conf["base_product_short"]
        ci.base_product.version = conf["base_product_version"]
        ci.base_product.type = conf.get("base_product_type", "ga").lower()

    ci.compose.label = compose_label
    ci.compose.type = compose_type
    ci.compose.date = compose_date or time.strftime("%Y%m%d", time.localtime())
    ci.compose.respin = compose_respin or 0
    ci.compose.id = ci.create_compose_id()
    return ci


def sortable(compose_id):
    """Convert ID to tuple where respin is an integer for proper sorting."""
    try:
        prefix, respin = compose_id.rsplit(".", 1)
        return prefix, int(respin)
    except Exception:
        return compose_id


def find_old_compose(old_compose_dirs, conf):
    composes = []
    release_short = conf['release_short']
    release_version = conf['release_version']
    release_type_suffix = conf.get("release_type_suffix", "")
    pattern = "%s-%s%s" % (release_short, release_version, release_type_suffix)
    for compose_dir in force_list(old_compose_dirs):
        if not os.path.isdir(compose_dir):
            continue
        # get all finished composes
        for i in list_files_starting_with(compose_dir, pattern):
            suffix = i[len(pattern):]
            if len(suffix) < 2 or not suffix[1].isdigit():
                continue
            path = os.path.join(compose_dir, i)
            status_path = os.path.join(path, "STATUS")
            if read_compose_status(status_path):
                composes.append((sortable(i), os.path.abspath(path)))
    if not composes:
        return None

    return sorted(composes)[-1][1]


def list_files_starting_with(directory, prefix):
    return [f for f in os.listdir(directory) if f.startswith(prefix)]


def read_compose_status(status_path):
    if not os.path.exists(status_path) or not os.path.isfile(status_path):
        return False
    try:
        with open(status_path, "r") as f:
            if f.read().strip() in ALLOWED_STATUSES:
                return True
    except Exception as e:
        print(e)
        return False
