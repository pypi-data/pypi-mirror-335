# -*- coding: UTF-8 -*-
"""client request Jenkins signature module"""
import configparser
import json
import os
import time

import jenkins
import urllib3
from logzero import logger

from .config import SOURCE_PATH
from .file import ensure_dir

urllib3.disable_warnings()

env = os.getenv("SERVER", "214")
conf = configparser.ConfigParser()
conf_dir = f"{SOURCE_PATH}/config/config-{env}.ini"
conf.read(conf_dir)

koji_task = {
    "8237": "sign-by-koji237-tag",
    "8238": "sign-by-koji238-tag",
    "8239": "sign-by-koji239-tag",
    "8241": "sign-by-koji241-tag",
    "8242": "sign-by-koji242-tag",
}


class JenkinsSign(object):
    """
    jenkins签名方法类
    """

    def __init__(self, config: dict):
        """参数初始化"""
        self.cur_day = time.strftime('%Y%m%d', time.localtime(time.time()))
        self.koji_ip = config.get("koji_ip")
        self.tag = config.get("tag", [])
        self.tag = self.tag if isinstance(self.tag, list) else [self.tag]
        self.url = "https://server.kylinos.cn:8085/"
        self.username = "xuyonghui"
        self.api_token = '11cc60ee65d385c61d433125ed447ae0ea'

    def _jenkins_sign(self, job_name, params, username, _token):
        """签名函数"""
        server = jenkins.Jenkins(self.url, username, _token or self.api_token)
        server._session.verify = False
        queue_id = server.build_job(job_name, parameters=params)
        queue = ""
        start_ts = int(time.time())

        while 1:
            now_ts = int(time.time())
            if now_ts - start_ts > 2.5 * 3600:
                logger.warning(f" {self.koji_ip} {params} Signing TimeOUT============")
                break
            job_info = server.get_job_info(job_name)
            num = job_info['builds'][0]['number']
            logger.info(f" {self.koji_ip} {params}签名任务No.:{num} ")
            build_info = server.get_build_info(job_name, num)
            if queue_id == build_info["queueId"]:
                if build_info['result'] == "SUCCESS":
                    queue = f"[{queue_id}] done"
                    break
                elif str(build_info['result']).lower() == "aborted":
                    logger.debug(f" {self.koji_ip} {params} Signing ABORTED {build_info['result']}")
                    break
                elif str(build_info['result']).lower() == "FAILURE".lower():
                    logger.debug(f" {self.koji_ip} {params} Signing FAILURE {build_info['result']}")
                    break
                logger.debug(f" {self.koji_ip} {params}/No.:{num} is signing . (10s) {build_info['result']}")
            else:
                logger.debug(f" {self.koji_ip} {params}/No.:{num} is pending. (10s) {build_info['result']}")
            time.sleep(10)
        return queue

    def get_sign_day(self, tag):
        days = [1, 2, 4, 8, 16, 32, 64, 128]
        last_run_at = 0
        if not last_run_at:
            cache_fp = os.path.dirname(__file__) + os.sep + "sign_his.json"
            if os.path.isfile(cache_fp):
                jd = json.loads(open(cache_fp, "r", encoding="utf-8").read())
                last_run_at = jd.get(tag)

        if last_run_at:
            exp_day = int(time.time() - last_run_at) // 86400
            for day in days:
                if exp_day < day:
                    return day
        return -1

    def set_sign_day(self, tag):

        cache_fp = os.path.dirname(__file__) + os.sep + "sign_his.json"
        ensure_dir(cache_fp)
        if os.path.isfile(cache_fp):
            jd = json.loads(open(cache_fp, "r", encoding="utf-8").read())
            jd[tag] = int(time.time())
            json.dump(jd, open(cache_fp, "w", encoding="utf-8"))
        else:
            json.dump({tag: int(time.time())}, open(cache_fp, "w", encoding="utf-8"))

    def sign_jenkins_job(self, job, koji_tag, tag, inherit):
        logger.debug(f" {self.koji_ip} {self.tag} 设置redis任务标志")
        day = self.get_sign_day(koji_tag)
        parameters = {"TAG": tag, "KICK_DAYS_BEFORE": day, "INHERIT": inherit}
        logger.info(f" {self.koji_ip} {self.tag} 参数：{parameters}")
        self._jenkins_sign(job, parameters, self.username, self.api_token)
        self.set_sign_day(koji_tag)

    def sign_work(self, flag, inherit=True):
        logger.info(f"开始签名 ==== ：{self.tag}")
        if flag == 'True':
            for tag in self.tag:
                job = koji_task.get(self.koji_ip.split(":")[-1].strip())
                koji_tag = f"{self.koji_ip[-3:]}_{tag}"
                if job:
                    self.sign_jenkins_job(job, koji_tag, tag, inherit)
                else:
                    logger.warning(f" 没有找到 {self.koji_ip} 对应的签名任务")
            logger.info(f"{self.koji_ip} {self.tag} 的签名工作完成")
        else:
            logger.info("标志位为空，不进行jenkins签名")
        return True
