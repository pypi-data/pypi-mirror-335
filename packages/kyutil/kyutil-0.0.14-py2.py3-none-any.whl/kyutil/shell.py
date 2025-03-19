# -*- coding: UTF-8 -*-
"""shell.py"""
import subprocess
import time
import traceback

import logzero


class Shell(object):
    """Shell(object)"""

    def __init__(self):
        self.ret_code = None
        self.ret_info = None
        self.err_info = None
        self.process = None

    def run_background(self, cmd):
        """
        后台执行命令
        @param cmd:
        @return:
        """
        self.process = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    def get_output(self):
        return self.process.stdout.read()

    def loading_output(self):
        return iter(self.process.stdout.readline, 'b')

    def kill(self):
        self.process.kill()


def run_command(cmd, error_message=None, logger=logzero.logger) -> bool:
    """
    执行Shell命令
    @param cmd:
    @param error_message:
    @param logger:
    @return:
    """
    try:
        print(f"== CMD:[{cmd}]")
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result.wait(7200)

        if result.returncode != 0:
            if error_message is not None:
                logger.info(error_message)
        else:
            return True
    except TimeoutError:
        logger.error(f"cmd Timeout: {cmd} ")
    except Exception as e:
        logger.error(f"cmd : {cmd} 运行失败。{e}")
    return False


def run_get_return(cmd, _logger=logzero.logger, timeout=3600) -> tuple:
    """
    函数功能：bash command执行，将所有命令stdout保存至变量，从中提取信息
    """
    try:
        all_stdout = ""
        print(f"== CMD:[{cmd}]")
        sign = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time_start = time.time()
        while sign.poll() is None:
            if time.time() - time_start > timeout:
                sign.kill()
            out = sign.stdout.readline()
            if out is None:
                continue
            else:
                result = out.decode(encoding='utf-8', errors='ignore') if isinstance(out, bytes) else str(out)
                if result.strip() and result != "" and result != "b''":
                    _logger.debug(result.strip())
            all_stdout = all_stdout + result + '\n'
        sign.wait()
        if sign.returncode != 0:
            _logger.error("ERROR CMD:[" + cmd + "]")
        return sign.returncode == 0, all_stdout
    except Exception as e:
        traceback.print_exc()
        _logger.error(str(e))
        raise SystemExit(cmd, str(e))


def run_get_return_once(cmd, _logger=logzero.logger) -> tuple:
    """
    函数功能：bash command执行，将所有命令stdout保存至变量，从中提取信息
    """
    try:
        all_stdout = ""
        _logger.info(f"CMD:[{cmd}]")
        sign = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = sign.stdout.readlines()
        for line in out:
            all_stdout = all_stdout + line.decode('utf-8').strip() + '\n'
        sign.wait()
        _logger.info(all_stdout.strip())
        if sign.returncode != 0:
            _logger.error("ERROR CMD:[" + cmd + "]")
        return sign.returncode == 0, all_stdout
    except Exception as e:
        traceback.print_exc()
        _logger.error(str(e))
        raise SystemExit(cmd, str(e))
