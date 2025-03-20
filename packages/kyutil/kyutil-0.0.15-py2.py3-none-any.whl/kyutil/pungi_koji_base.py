# -*- coding: UTF-8 -*-
"""client iso integration build module"""
import json
import os
import time

import kobo.conf
import koji
from git import Repo
from productmd import ComposeInfo

from .paths import BasePaths
from .pungi_util import get_compose_info, find_old_compose

ROOT_PATH_ISO_PATH = "/opt/integration_iso_files/"
ALLOWED_STATUSES = ("STARTED", "FINISHED", "FINISHED_INCOMPLETE", "DOOMED")


class PungiKojiBase(object):
    """集成构建基类"""

    def __init__(self, **kwargs):
        """init初始化函数-基类"""
        self.config_repo_dir = f"{ROOT_PATH_ISO_PATH}auto_os/"
        self.config_dir = os.path.join(self.config_repo_dir, kwargs.get('config_dir', '').lstrip("/"))
        self.config_name = kwargs.get('config_name')
        self.config_filepath = os.path.join(self.config_dir, self.config_name)
        self.conf = self.load_config()
        self.ci_base = ComposeInfo()
        self.load_compose()
        self.path = BasePaths(self.get_work_dir())

        self.profile = None

    def check(self):
        self.check_koji_profile()

    def check_koji_profile(self):
        try:
            self.profile = self.conf.get("koji_profile", None)
            if not self.profile:
                raise RuntimeError(f"koji_profile必须指定，请检查 {self.config_filepath} 中是否配置 koji_profile ！")
            koji.read_config(self.profile)
        except Exception as e:
            raise RuntimeError(f"{e}，检查{self.config_filepath} 中配置的 koji_profile是否在编译机配置 ！")

    def load_compose(self):
        res = self.get_old_compose()
        if res:
            self.ci_base.load(res)
        else:
            self.ci_base = None

    def load_config(self, defaults=None):
        """Open and load configuration file form .conf or .json file."""
        if not os.path.exists(self.config_filepath):
            return None
        conf = kobo.conf.PyConfigParser()
        conf.load_from_dict(defaults)
        if self.config_filepath.endswith(".json"):
            with open(self.config_filepath) as f:
                conf.load_from_dict(json.load(f))
            conf.opened_files = [self.config_filepath]
            conf._open_file = self.config_filepath
        else:
            conf.load_from_file(self.config_filepath)
        return conf

    def get_work_dir(self, topdir="/mnt/koji/compose/", compose_type="production", compose_date=None,
                     compose_respin=None, compose_label=None):
        respin = None
        if self.ci_base:
            if self.ci_base.compose.date == time.strftime("%Y%m%d", time.localtime()):
                respin = int(self.ci_base.compose.respin) + 1
            else:
                respin = None
        if compose_respin:
            respin = compose_respin
        ci = get_compose_info(self.conf, compose_type, compose_date, respin, compose_label)
        ci.compose.id = ci.create_compose_id()
        compose_dir = os.path.join(topdir, ci.compose.id)

        return compose_dir

    def get_old_compose(self):
        res = find_old_compose("/mt/koji/compose/", self.conf)
        if not res or not os.path.exists(res):
            return None
        conf = BasePaths(res).work.composeinfo()
        if not os.path.exists(conf):
            return None
        return conf

    def link_compose(self, compose_dir):
        """
        :param compose_dir:
        """
        work_dir = self.path.topdir()
        try:
            os.symlink(work_dir, compose_dir.rstrip('/'))
            print(f"Symbolic link created: {work_dir} -> {compose_dir}")
        except OSError as e:
            print(f"Failed to create symbolic link: {e}")

    def update_config_repo(self, commit='HEAD'):
        """
        """
        config_repo = Repo(self.config_repo_dir)
        config_repo.git.reset('--hard', commit)
        current_commit = config_repo.commit()
        config_repo.remote().fetch()
        config_repo.remote().pull()
        latest_commit = config_repo.commit()
        if current_commit != latest_commit:
            print(f"config_repo updated: {current_commit} -> {latest_commit}")
        else:
            print(f"config_repo not updated: {current_commit}")
