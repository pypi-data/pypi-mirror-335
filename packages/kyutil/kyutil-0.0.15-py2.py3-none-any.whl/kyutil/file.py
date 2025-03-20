# -*- coding: UTF-8 -*-
import hashlib
import json
import os
import shutil
import stat
import xml.etree.ElementTree as ET

from logzero import logger

special_characters = ['、', ':', '；', '。', '？', '（', ]


def gen_file_tree(path: str, tmp_path: str = ""):
    """
    控件参考地址为：  https://ng-zorro.gitee.io/components/tree/zh
    生成iso中的文件树，符合前端控件数据结构
    @param path:
    @param tmp_path:
    @return:
    title	    标题
    key	        整个树范围内的所有节点的 key 值不能重复且不为空！
    children	子节点
    isLeaf  	设置为叶子节点(叶子节点不可被拖拽模式放置)
    [{
      title: '0-0-1',
      key: '0-0-1',
      children: [
        { title: '0-0-1-0', key: '0-0-1-0', isLeaf: true },
        { title: '0-0-1-1', key: '0-0-1-1', isLeaf: true },
        { title: '0-0-1-2', key: '0-0-1-2', isLeaf: true }
      ]
    },
    {
      title: '0-0-2',
      key: '0-0-2',
      isLeaf: true
    }]
    """
    files = []
    if os.path.exists(path):
        for _d in os.listdir(path):
            _p = path + os.sep + _d
            node = dict()
            if os.path.isdir(_p):
                node["title"] = _d
                node["key"] = _p.replace(tmp_path, "")
                node["children"] = []
                node["children"].extend(gen_file_tree(_p, tmp_path))
            elif os.path.isfile(_p):
                node["title"] = _d
                node["key"] = _p.replace(tmp_path, "")
                node["isLeaf"] = True
            if node:
                files.append(node)
    return files


def ensure_dir(fp):
    """
    确保目录存在
    Args:
        fp: 文件路径，可以是文件路径，也可以是目录

    Returns:

    """
    if not fp:
        return

    dir_fp = os.path.dirname(fp)
    if not os.path.isdir(dir_fp):
        os.makedirs(dir_fp)
    return os.path.isdir(os.path.dirname(fp))


def remove_file(fp: str) -> bool:
    """
    删除文件
    Args:
        fp: 文件路径

    Returns:

    """
    if fp and os.path.isfile(fp):
        os.remove(fp)
    return not os.path.isfile(fp)


def _item_symlinks(srcname, symlinks, dstname, srcobj, ignore_dangling_symlinks, src_entry, ignore, copy_function, dirs_exist_ok):
    linkto = os.readlink(srcname)
    if symlinks:
        os.symlink(linkto, dstname)
        shutil.copystat(srcobj, dstname, follow_symlinks=not symlinks)
    else:
        if not os.path.exists(linkto) and ignore_dangling_symlinks:
            return
        if src_entry.is_dir():
            my_copytree(srcobj, dstname, symlinks, ignore,
                        copy_function, ignore_dangling_symlinks,
                        dirs_exist_ok)
        else:
            copy_function(srcobj, dstname)


def _item(src_entry, ignored_names, src, dst, use_src_entry, symlinks, ignore_dangling_symlinks, ignore, copy_function, dirs_exist_ok, errors):
    if src_entry.name in ignored_names:
        return
    srcname = os.path.join(src, src_entry.name)
    dstname = os.path.join(dst, src_entry.name)
    srcobj = src_entry if use_src_entry else srcname
    try:
        is_symlink = src_entry.is_symlink()
        if is_symlink and os.name == 'nt':
            lstat = src_entry.stat(follow_symlinks=False)
            if lstat.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT:
                is_symlink = False
        if is_symlink:
            _item_symlinks(srcname, symlinks, dstname, srcobj, ignore_dangling_symlinks, src_entry, ignore, copy_function, dirs_exist_ok)
        elif src_entry.is_dir():
            my_copytree(srcobj, dstname, symlinks, ignore, copy_function,
                        ignore_dangling_symlinks, dirs_exist_ok)
        else:
            copy_function(srcobj, dstname)
    except shutil.Error as err:
        errors.extend(err.args[0])
    except OSError as why:
        errors.append((srcname, dstname, str(why)))


def _copytree(entries, src, dst, symlinks, ignore, copy_function,
              ignore_dangling_symlinks, dirs_exist_ok=False):
    if ignore is not None:
        ignored_names = ignore(os.fspath(src), [x.name for x in entries])
    else:
        ignored_names = set()

    os.makedirs(dst, exist_ok=dirs_exist_ok)
    errors = []
    use_src_entry = copy_function is shutil.copy2 or copy_function is shutil.copy

    for src_entry in entries:
        _item(src_entry, ignored_names, src, dst, use_src_entry, symlinks, ignore_dangling_symlinks, ignore, copy_function, dirs_exist_ok, errors)

    try:
        shutil.copystat(src, dst)
    except OSError as why:
        if getattr(why, 'winerror', None) is None:
            errors.append((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)
    return dst


def my_copytree(src, dst, symlinks=False, ignore=None, copy_function=shutil.copy2,
                ignore_dangling_symlinks=False, dirs_exist_ok=False):
    with os.scandir(src) as itr:
        entries = list(itr)
    return _copytree(entries=entries, src=src, dst=dst, symlinks=symlinks,
                     ignore=ignore, copy_function=copy_function,
                     ignore_dangling_symlinks=ignore_dangling_symlinks,
                     dirs_exist_ok=dirs_exist_ok)


def reset_dirs(remake_dir):
    """
    函数功能：重置创建多级目录
    函数参数：remake_dir - 需要重建的目录
    函数返回值： 无
    """
    logger.info("重置目录：" + remake_dir)
    if os.path.exists(remake_dir):
        shutil.rmtree(remake_dir)
    try:
        os.makedirs(remake_dir, exist_ok=True)
    except Exception as err:
        logger.info("Create directories error: {0}".format(err))
        raise FileExistsError("Create directories error: {0}".format(err))


def delete_dirs(useless_dir, logger_=logger):
    """
    函数功能：通用文件删除
    函数参数：useless_dir - 需要删除的目录或文件
    函数返回值：无
    """
    if not os.path.exists(useless_dir):
        # 仅提示不报错
        logger_.warning(f"要删除的目录：{useless_dir} 不存在!")
    try:
        if os.path.isdir(useless_dir):
            shutil.rmtree(useless_dir)
            logger_.info(f"删除目录：{useless_dir}")
        if os.path.isfile(useless_dir):
            os.remove(useless_dir)
            logger_.info(f"删除文件：{useless_dir}")
    except Exception as err:
        logger_.error(" == Delete directories error: {0}".format(err))
        raise FileExistsError("Delete directories error: {0}".format(err))


def move_dirs(source, target):
    """
    函数功能：通用文件移动
    函数参数：source_dir-源目录或文件/target_dir-目标目录或文件
    函数返回值: 无
    """
    if not os.path.exists(source):
        logger.error(f"{source} not exist!")
        raise FileNotFoundError(f"src [{source}] not exist!")
    try:
        ensure_dir(target)
        if not os.path.isdir(target):
            os.makedirs(target)
        if os.path.isdir(source):
            for file in os.listdir(source):
                shutil.move(os.path.join(source, file), os.path.join(target, file))
        if os.path.isfile(source):
            shutil.move(source, target)
    except Exception as err:
        logger.error("Move directories error: {0}".format(err))
        raise FileExistsError("Move directories error: {0}".format(err))


def copy_dirs(source, target, logger_=logger):
    """
    函数功能：通用文件复制
    函数参数：source_dir-源目录或文件/target_dir-目标目录或文件
    函数返回值：
    """
    if not os.path.exists(source):
        logger_.info(f"Can't COPY. src [{source}] not exist!")
        raise FileNotFoundError(f"Can't COPY. src [{source}] not exist!")
    try:
        ensure_dir(target)
        if os.path.isdir(source):
            for file in os.listdir(source):
                if os.path.isdir(os.path.join(source, file)):
                    my_copytree(os.path.join(source, file), os.path.join(target, file), dirs_exist_ok=True)
                elif os.path.isfile(os.path.join(source, file)):
                    shutil.copy(os.path.join(source, file), os.path.join(target, file))
                else:
                    logger_.warning(f"文件不存在: {file}")
        elif os.path.isfile(source):
            shutil.copy(source, target)
            if os.path.isfile(target):
                logger_.info(f"文件复制成功：{source} -> {target}")
            else:
                raise RuntimeError(f"文件复制失败：{source} -> {target}")
        else:
            logger_.warning(f"文件不存在: {source}")
    except Exception as err:
        logger_.error("复制命令出错: {0}".format(err))
        raise FileExistsError("复制命令出错: {0}".format(err))


def file_str_switch(_file, old_str, new_str, _g=1, _logger=logger, reason=None):
    """
    函数功能：替换文件指定行内容
    函数参数：file：要更新的文件名称；old_str：被替换的内容；new_str：表示替换后的内容；
    _g默认参数为1，表示只替换第一个匹配到的字符串；
    如果参数为_g = 'g'，则表示全文替换，排除携带#的行；
    函数返回值：无
    """
    _logger.info(f'【FILE_MODIFY】{reason}: 将 {_file} 中 {old_str} 替换为 {new_str}')
    with open(_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(_file, "w", encoding="utf-8") as f_w:
        n = 0
        if _g == 1:
            for line in lines:
                if old_str in line:
                    f_w.write(new_str)
                    n += 1
                    break
                f_w.write(line)
                n += 1
            for i in range(n, len(lines)):
                f_w.write(lines[i])
        elif _g == "g":
            for line in lines:
                if old_str in line:
                    line = new_str
                f_w.write(line)


def file_write(_file, _str):
    """
    函数功能：追加写指定文件
    函数参数：file - 文件路径；new_str - 新字符串
    函数返回值：无
    """
    if not os.path.isdir(os.path.dirname(_file)):
        os.makedirs(os.path.dirname(_file), exist_ok=True)
    with open(_file, "a+", encoding="utf-8") as f:
        json.dumps(_str, indent=4, separators=(",", ":"))
        f.write(_str)
        f.write(os.linesep)


def read_sha256sum_from_file(file_path):
    try:
        with open(file_path) as f:
            sha256sum_line = f.readline()
        return sha256sum_line.split()[0]
    except Exception as e:
        print("读取sha256sum失败，原因：", e)
        return ""


def get_file_list(file_path, exclude_keywords=None):
    if exclude_keywords is None:
        exclude_keywords = []
    for parent, dir_names, file_names in os.walk(file_path):
        dir_names.sort()
        for filename in file_names:
            if any(keyword in filename for keyword in exclude_keywords):
                continue
            yield parent, filename


def get_file_size(fp: str) -> int:
    """
    获取文件大小
    Args:
        fp:

    Returns:

    """
    if os.path.isfile(fp):
        return os.path.getsize(fp)
    return -1


def get_file_sha256sum(fp: str) -> str:
    """
    获取文件sha256
    Args:
        fp: 文件路径

    Returns:

    """
    if os.path.isfile(fp):
        m = hashlib.sha256()  # 创建md5对象
        with open(fp, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                m.update(data)  # 更新md5对象

        return m.hexdigest()  # 返回md5对象
    else:
        raise FileExistsError("File not exists")


def get_comps_list(fp: str) -> set:
    """
    获取文件大小comps文件包列表
    """
    package_names = set()
    if not os.path.exists(fp):
        return package_names
    tree = ET.parse(f'{fp}')
    root = tree.getroot()

    # 遍历XML节点并提取所有包名
    for group in root.findall('.//group'):
        for package in group.findall('.//packagereq'):
            pkg_name = package.text
            package_names.add(pkg_name)
    return package_names


def get_ks_list(fp: str) -> set:
    """
    获取文件大小comps文件包列表
    """
    ks_list = set()
    if not os.path.exists(fp):
        return ks_list
    with open(fp, "r") as f:
        for line in f.readlines()[2:-1]:
            line = line[:-1]
            ks_list.add(line)
    return ks_list


def recursive_chmod(path, mode):
    """
    递归修改目录和文件的所有者权限
    """
    if not os.path.exists(path):
        return
    try:
        os.chmod(path, mode)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files + dirs:
                    recursive_chmod(os.path.join(root, file), mode)
    except Exception as e:
        logger.warning(f"递归修改目录和文件的所有者权限 失败: [{e}]")


def get_files(path_, index_="", suffix=None):
    f_ = list()
    if not os.path.isdir(path_):
        return f_
    for root, dirs, files in os.walk(path_):
        for file in files:
            if index_ in file:
                f_.append(os.path.join(root, file))
    return [x for x in f_ if x.endswith(suffix)]
