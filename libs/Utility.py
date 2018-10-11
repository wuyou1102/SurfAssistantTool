# -*- encoding:UTF-8 -*-
import os
import sys
import logging
import ADB_Command as Adb
import FastbootCommand as fastboot
from ThreadManager import append_work, is_alive
import re
import time

__log = logging.getLogger(__name__)


def get_timestamp(time_fmt='%Y_%m_%d-%H_%M_%S', t=None):
    t = t if t else time.time()
    return time.strftime(time_fmt, time.localtime(t))


def makedirs(path, *paths):
    p = os.path.join(path, *paths)
    if not os.path.exists(p):
        os.makedirs(p)
    return p


def get_workspace():
    return os.path.abspath(os.path.dirname(sys.argv[0]))


def get_devices():
    devices = list()
    lines = os.popen(Adb.devices()).readlines()
    for line in lines:
        __log.debug(line)
        if 'device' in line and 'List of' not in line:
            devices.append(line[:line.index('\t')])
    return devices


def get_fastboots():
    devices = list()
    lines = os.popen(fastboot.devices()).readlines()
    for line in lines:
        __log.debug(line)
        if 'fastboot' in line:
            devices.append(line[:line.index('\t')])
    return devices


def find_in_string(pattern, string):
    try:
        result = re.findall(pattern, string)[0]
    except IndexError:
        result = 'Illegal'
        __log.error('Can not find the pattern.')
        __log.error("Pattern:%s" % pattern)
        __log.error("String :" + repr(string))

    finally:
        return result


def run_cmd(cmd):
    __log.info(u"Run Command:%s" % cmd)
    return os.popen3(cmd)
