# -*- encoding:UTF-8 -*-
import os
import sys
import logging
import platform

__log = logging.getLogger(__name__)
__adb = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),
                     "adb.exe") if platform.system() == "Windows" else "adb"

def pull(remote, local, serial=''):
    if serial:
        return '{adb} -s {serial} pull {remote} {local}'.format(adb=__adb,
                                                                serial=serial,
                                                                remote=remote, local=local)
    return '{adb} pull {remote} {local}'.format(adb=__adb, remote=remote, local=local)


def push(local, remote, serial=''):
    if serial:
        return '{adb} -s {serial} push {local} {remote}'.format(adb=__adb,
                                                                serial=serial,
                                                                remote=remote, local=local)
    return '{adb} push {local} {remote}'.format(adb=__adb, remote=remote, local=local)


def reboot(serial='', mode=''):
    if serial:
        if mode:
            return '{adb} -s {serial} reboot-{mode}'.format(adb=__adb, serial=serial, mode=mode)
        return '{adb} -s {serial} reboot'.format(adb=__adb, serial=serial)
    if mode:
        return '{adb} reboot-{mode}'.format(adb=__adb, mode=mode)
    return '{adb} reboot'.format(adb=__adb)


def wait_for_device(serial=''):
    if serial:
        return '{adb} -s {serial} wait-for-device'.format(adb=__adb, serial=serial)
    return '{adb} wait-for-device'.format(adb=__adb)


def am_start(package, activity, serial=''):
    if serial:
        if activity:
            return '{adb} -s {serial} shell am start -n {package}/{activity}'.format(adb=__adb, serial=serial,
                                                                                     package=package, activity=activity)
        return '{adb} -s {serial} shell am start {package}'.format(adb=__adb, serial=serial, package=package)
    else:
        if activity:
            return '{adb} shell am start -n {package}/{activity}'.format(adb=__adb, package=package, activity=activity)
        return '{adb} shell am start {package}'.format(adb=__adb, package=package)


def force_stop(package, serial=''):
    if serial:
        return '{adb} -s {serial} shell am force-stop {package}'.format(adb=__adb, serial=serial, package=package)
    else:
        return '{adb} shell am force-stop {package}'.format(adb=__adb, package=package)


def root(serial=''):
    if serial:
        return '{adb} -s {serial} root'.format(adb=__adb, serial=serial)
    return '{adb} root'.format(adb=__adb)


def devices():
    return '{adb} devices'.format(adb=__adb)


def shell_command(cmd, serial=''):
    if serial:
        return '{adb} -s {serial} shell \"{command}\"'.format(adb=__adb, serial=serial, command=cmd)
    return '{adb} shell \"{command}\"'.format(adb=__adb, command=cmd)


def shell(serial=''):
    if serial:
        return '{adb} -s {serial} shell'.format(adb=__adb, serial=serial)
    return '{adb} shell'.format(adb=__adb)
