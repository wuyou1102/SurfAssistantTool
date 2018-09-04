# -*- encoding:UTF-8 -*-
import sys
import wx
import ADB_Command as Adb
import os
import logging
from libs import Utility
import time
import re

pattern = re.compile(r'currtnt frame = (\d+)-----total frame = (\d+)\r\n')
log = logging.getLogger(__name__)


class Frame(wx.Frame):
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Surf V0.0.1", pos=wx.DefaultPosition,
                          size=wx.Size(800, 600), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.panel = Panel(self)


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 300),
                          style=wx.TAB_TRAVERSAL)
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        DeviceSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Device"), wx.HORIZONTAL)
        AndroidSizer = wx.BoxSizer(wx.VERTICAL)
        DeviceListBoxChoices = Utility.get_devices()
        self.DeviceListBox = wx.ListBox(DeviceSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                        DeviceListBoxChoices, 0)
        self.DeviceListBox.Bind(wx.EVT_LISTBOX, self.on_select_item)
        self.RefreshButton = wx.Button(DeviceSizer.GetStaticBox(), wx.ID_ANY, u"Refresh", wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        self.RefreshButton.Bind(wx.EVT_BUTTON, self.on_refresh)
        ArtosynSizer = wx.StaticBoxSizer(wx.StaticBox(DeviceSizer.GetStaticBox(), wx.ID_ANY, u"Artosyn8020"),
                                         wx.VERTICAL)
        self.ST_Artosyn = wx.StaticText(ArtosynSizer.GetStaticBox(), wx.ID_ANY, u"请先选择Andrid设备", wx.DefaultPosition,
                                        wx.DefaultSize, 0)
        self.ST_Artosyn.Wrap(-1)

        ButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.open_button = wx.Button(ArtosynSizer.GetStaticBox(), wx.ID_ANY, u"Open", wx.DefaultPosition,
                                     wx.DefaultSize, 0)
        self.close_button = wx.Button(ArtosynSizer.GetStaticBox(), wx.ID_ANY, u"Close", wx.DefaultPosition,
                                      wx.DefaultSize, 0)
        self.root_button = wx.Button(ArtosynSizer.GetStaticBox(), wx.ID_ANY, u"Root", wx.DefaultPosition,
                                     wx.DefaultSize, 0)
        self.wakeup_button = wx.Button(ArtosynSizer.GetStaticBox(), wx.ID_ANY, u"WakeUp", wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        self.open_button.Bind(wx.EVT_BUTTON, self.on_open)
        self.close_button.Bind(wx.EVT_BUTTON, self.on_close)
        self.root_button.Bind(wx.EVT_BUTTON, self.on_root)
        self.wakeup_button.Bind(wx.EVT_BUTTON, self.on_wakeup)
        ButtonSizer.Add(self.open_button, 0, wx.ALL, 0)
        ButtonSizer.Add(self.close_button, 0, wx.ALL, 0)
        ButtonSizer.Add(self.root_button, 0, wx.ALL, 0)
        ButtonSizer.Add(self.wakeup_button, 0, wx.ALL, 0)

        UpgradeSizer = wx.StaticBoxSizer(wx.StaticBox(ArtosynSizer.GetStaticBox(), wx.ID_ANY, u"Upgrade"), wx.VERTICAL)

        Up_St_Sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.upgarde_gauge = wx.Gauge(UpgradeSizer.GetStaticBox(), wx.ID_ANY, 1000, wx.DefaultPosition, wx.DefaultSize,
                                      wx.GA_HORIZONTAL)
        self.upgarde_gauge.SetValue(0)
        Up_St_Sizer.Add(self.upgarde_gauge, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.upgrade_button = wx.Button(UpgradeSizer.GetStaticBox(), wx.ID_ANY, u"Start", wx.DefaultPosition,
                                        wx.DefaultSize, 0)
        self.upgrade_button.Bind(wx.EVT_BUTTON, self.on_upgrade)
        Up_St_Sizer.Add(self.upgrade_button, 0, wx.LEFT, 5)
        self.FilePicker = wx.FilePickerCtrl(UpgradeSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select a file",
                                            u"*.bin", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE)
        UpgradeSizer.Add(Up_St_Sizer, 1, wx.EXPAND, 5)
        UpgradeSizer.Add(self.FilePicker, 0, wx.EXPAND | wx.ALL, 0)

        AndroidSizer.Add(self.DeviceListBox, 1, wx.EXPAND | wx.ALL, 0)
        AndroidSizer.Add(self.RefreshButton, 0, wx.EXPAND | wx.ALL, 0)
        ArtosynSizer.Add(self.ST_Artosyn, 0, wx.ALL, 0)
        ArtosynSizer.Add(ButtonSizer, 1, wx.EXPAND, 0)
        ArtosynSizer.Add(UpgradeSizer, 0, wx.EXPAND, 0)
        DeviceSizer.Add(AndroidSizer, 1, wx.EXPAND, 5)
        DeviceSizer.Add(ArtosynSizer, 2, wx.EXPAND | wx.LEFT, 5)

        MessageSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Message"), wx.VERTICAL)

        self.TC_message = wx.TextCtrl(MessageSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                      wx.DefaultSize, 0)
        MessageSizer.Add(self.TC_message, 1, wx.ALL | wx.EXPAND, 0)

        MainSizer.Add(DeviceSizer, 1, wx.EXPAND | wx.ALL, 5)
        MainSizer.Add(MessageSizer, 5, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.SetSizer(MainSizer)
        self.Layout()

    def on_wakeup(self, event):
        os.system(Adb.shell_command(cmd="input keyevent 26",
                                    serial=self.DeviceListBox.GetStringSelection()))
        # os.system(Adb.shell(cmd="input keyevent 82",
        #                     serial=self.DeviceListBox.GetStringSelection()))

    def on_open(self, event):
        os.system(Adb.shell_command(cmd="echo 1 > /sys/bus/platform/drivers/artosyn_ar8020/soc:ar8020/enable",
                                    serial=self.DeviceListBox.GetStringSelection()))
        self.update_8020_state()

    def on_close(self, event):
        os.system(Adb.shell_command(cmd="echo 0 > /sys/bus/platform/drivers/artosyn_ar8020/soc:ar8020/enable",
                                    serial=self.DeviceListBox.GetStringSelection()))
        self.update_8020_state()

    def on_root(self, event):
        def root_device():
            os.system(Adb.root(serial=self.DeviceListBox.GetStringSelection()))
            os.system(Adb.shell_command(cmd="setenforce 0", serial=self.DeviceListBox.GetStringSelection()))
            self.update_8020_state()

        Utility.append_work(target=root_device, allow_dupl=False)

    def on_refresh(self, event):
        def refresh():
            self.DeviceListBox.Set(Utility.get_devices())

        self.DeviceListBox.Set(["Refreshing"])
        Utility.append_work(target=refresh, allow_dupl=False)

    def on_select_item(self, event):
        Utility.append_work(target=self.update_8020_state, allow_dupl=False)

    def update_8020_state(self):
        self.ST_Artosyn.SetLabel(self.check_8020_state(serial=self.DeviceListBox.GetStringSelection()))

    def check_8020_state(self, serial):
        log.debug("check the AR 8020 state in device:%s" % serial)
        out = os.popen(
            Adb.shell_command(cmd="cat /sys/bus/platform/drivers/artosyn_ar8020/soc:ar8020/enable",
                              serial=serial)).read()
        if out == "1\n":
            return u"AR8020 已经打开"
        elif out == "0\n":
            return u"AR8020 已经关闭"
        else:
            return u"请检查设备是否已经ROOT,或者设备并不是Surf"

    def on_upgrade(self, event):
        def upgrade():
            self.DeviceListBox.Disable()
            self.upgrade_button.Disable()
            bin_file = self.FilePicker.GetPath()
            log.debug("AR8020 File:%s" % bin_file)
            if bin_file and os.path.exists(bin_file):
                log.debug("AR8020 File:%s" % bin_file)
                os.system(Adb.push(local=bin_file, remote="/data/local/tmp/8020.bin",
                                   serial=self.DeviceListBox.GetStringSelection()))
                self.open_8020_before_upgrade()
                self.update_8020_state()
                import subprocess
                p = subprocess.Popen(Adb.shell_command(cmd="upgrade_ar8020 /data/local/tmp/8020.bin",
                                                       serial=self.DeviceListBox.GetStringSelection()),
                                     stdout=subprocess.PIPE,
                                     bufsize=1)
                while True:
                    data = p.stdout.readline()  # block/wait
                    log.debug(repr(data))
                    if "get file size" in data:
                        self.ST_Artosyn.SetLabel(u"Upgrading...")
                    elif "upgrade successed" in data:
                        self.ST_Artosyn.SetLabel(u"Upgrade complete,Wait for reboot AR8020")
                        break
                    else:
                        cur, total = Utility.find_in_string(pattern=pattern, string=data)
                        cur, total = float(cur), int(total)
                        self.upgarde_gauge.SetValue(cur / total * 1000)
                        print cur / total * 1000
                    time.sleep(0.01)
                os.system(Adb.shell_command(cmd="echo 0 > /sys/bus/platform/drivers/artosyn_ar8020/soc:ar8020/enable",
                                            serial=self.DeviceListBox.GetStringSelection()))
                time.sleep(1)
                os.system(Adb.shell_command(cmd="echo 1 > /sys/bus/platform/drivers/artosyn_ar8020/soc:ar8020/enable",
                                            serial=self.DeviceListBox.GetStringSelection()))
                self.update_8020_state()
            else:
                log.warn("Can not find Bin File ,Skip.")
            self.DeviceListBox.Enable()
            self.upgrade_button.Enable()

        Utility.append_work(target=upgrade, allow_dupl=False)

    def open_8020_before_upgrade(self):
        os.system(Adb.root(serial=self.DeviceListBox.GetStringSelection()))
        os.system(Adb.shell_command(cmd="setenforce 0", serial=self.DeviceListBox.GetStringSelection()))
        res = self.check_8020_state(serial=self.DeviceListBox.GetStringSelection())
        if res == u"AR8020 已经打开":
            return True
        else:
            os.system(Adb.shell_command(cmd="echo 1 > /sys/bus/platform/drivers/artosyn_ar8020/soc:ar8020/enable",
                                        serial=self.DeviceListBox.GetStringSelection()))
            time.sleep(3)
            return self.open_8020_before_upgrade()
