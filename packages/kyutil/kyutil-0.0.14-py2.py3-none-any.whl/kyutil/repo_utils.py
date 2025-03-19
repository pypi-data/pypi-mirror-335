# -*- coding: UTF-8 -*-
import logging
import os
import shutil

from bs4 import BeautifulSoup

from .base import sha256_file
from .http_util import send_request
from .util_rpm_info import is_url

REPODATA = "repodata"


def get_map_name2url4a(_link) -> dict:
    """
    将url或者路径，封装为字典
    Args:
        _link: /a/

    Returns:
        {
            "1.txt":"/a/1.txt",
            "2.txt":"/a/2.txt",
        }
    """
    if is_url(_link):
        r = send_request(_link, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        _name_href_map = {}
        soup_a_list = soup.find_all("a")
        for soup_a in soup_a_list:
            if '..' in soup_a.string:
                continue
            _name_href_map[soup_a.string] = _link.rstrip('/') + '/' + soup_a.get("href")
        return _name_href_map

    elif os.path.isdir(_link):
        _name_href_map = {}
        soup_a_list = os.listdir(_link)
        for soup_a in soup_a_list:
            if os.path.isdir(_link + os.sep + soup_a):
                soup_a = soup_a.rstrip("/") + "/"
            _name_href_map[soup_a] = _link.rstrip('/') + '/' + soup_a

        return _name_href_map
    return {}


def find_sub_repo(url="", map_name2link=None):
    if not any([url, map_name2link]):
        return []
    candidate_link_repodata = []
    map_name2link = map_name2link or get_map_name2url4a(url)

    if f"{REPODATA}/" in map_name2link:  # repodata同一层级或更下一般不会再有repodata
        return [{"name": "MainRepo", "url": map_name2link[f"{REPODATA}/"].replace(f"{REPODATA}/", "")}]
    for name, link in map_name2link.items():
        if name.endswith('/'):  # 目录
            candidate_link_repodata.extend(find_sub_repo(map_name2link=get_map_name2url4a(link)))
    if url:
        candidate_link_repodata = [{"name": link.replace(url, ""), "url": link} for link in candidate_link_repodata]
    return candidate_link_repodata


def rebuild_pkg_one(repo_path, packages_path, rpm_info_obj, _logger=logging):
    """基于Repodata重建仓库 --> 恢复单个软件包
    Args:
        repo_path: 指定仓库的地址，会基于repodata中Packages表中的location_href字段，去找到Rpm包在此目录中的相对位置(Packages)
        packages_path: 指定需要从哪里拉取软件包，会基于rpm_info_obj中的数据，拼接后面的路径
        rpm_info_obj: 保存单个Rpm包信息的对象
        _logger:
    Example:
        rebuild_pkg_one("repo", "/opt/integration_iso_files/packages", rpm_info_obj)
            其中repo_path中不应包含Packages字段，会基于repodata中的数据自动加上
    """
    path_list = [
        packages_path,
        rpm_info_obj.rpm_name[0],
        rpm_info_obj.rpm_name,
        rpm_info_obj.version,
        rpm_info_obj.release,
        rpm_info_obj.arch,
        rpm_info_obj.sha256sum[:6],
        rpm_info_obj.fullname
    ]
    rpm_path = os.path.join(*path_list)
    target_path = os.path.join(repo_path, rpm_info_obj.filepath)
    if not os.path.exists(os.path.dirname(target_path)):
        os.makedirs(os.path.dirname(target_path))
    if os.path.exists(rpm_path):
        shutil.copy(rpm_path, target_path)
    else:
        _logger.error(f"Rpm源不存在[{rpm_path}]！")
        return False
    if sha256_file(target_path) != rpm_info_obj.sha256sum:
        _logger.error(f"复制文件[{os.path.basename(target_path)}]失败，哈希值不同！")
        return False
    return True
