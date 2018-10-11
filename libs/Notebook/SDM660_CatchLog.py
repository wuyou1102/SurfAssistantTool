# -*- encoding:UTF-8 -*-
import wx
from libs import Utility
import os
from libs import ADB_Command as adb
from libs import FastbootCommand as fastboot
import re
import time
import logging
u
log = logging.getLogger(__name__)


class AndroidCatchLog(wx.Panel):
    def __init__(self, parent):
        self.name = "Android日志"