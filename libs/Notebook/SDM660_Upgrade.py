# -*- encoding:UTF-8 -*-
import wx
from libs import Utility
import os
from libs import ADB_Command as adb
from libs import FastbootCommand as fastboot
import re
import time
import logging

log = logging.getLogger(__name__)


class AndroidUpgrade(wx.Panel):
    def __init__(self, parent):
        self.name = u"Android升级"
        self.upgrade_list = list()
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)
        MainSizer = wx.BoxSizer(wx.HORIZONTAL)
        LeftSizer = wx.BoxSizer(wx.VERTICAL)
        RightSizer = wx.BoxSizer(wx.VERTICAL)
        devices_sizer = self.__init_devices_sizer()
        upgrade_sizer = self.__init_upgrade_sizer()
        self.upgrade_info_sizer = self.__init_upgrade_info_sizer()
        LeftSizer.Add(devices_sizer, 1, wx.EXPAND | wx.ALL, 0)
        RightSizer.Add(upgrade_sizer, 0, wx.EXPAND | wx.ALL, 0)
        RightSizer.Add(self.upgrade_info_sizer, 1, wx.EXPAND | wx.ALL, 0)

        MainSizer.Add(LeftSizer, 1, wx.EXPAND | wx.ALL, 1)
        MainSizer.Add(RightSizer, 4, wx.EXPAND | wx.ALL, 1)

        self.SetSizer(MainSizer)
        self.Layout()

    def __init_devices_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"设备"), wx.VERTICAL)
        device_choices = Utility.get_devices()
        fastboot_choices = Utility.get_fastboots()
        d_tilte = wx.StaticText(self, wx.ID_ANY, u"Android Devices", wx.DefaultPosition, wx.DefaultSize,
                                wx.ALIGN_CENTER)
        f_title = wx.StaticText(self, wx.ID_ANY, u"Fastboot Devices", wx.DefaultPosition, wx.DefaultSize,
                                wx.ALIGN_CENTER)
        self.lb_devices = wx.ListBox(sizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                     device_choices, style=wx.LB_EXTENDED)
        self.lb_fastboot = wx.ListBox(sizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                      fastboot_choices, style=wx.LB_EXTENDED)
        button = wx.Button(sizer.GetStaticBox(), wx.ID_ANY, u"刷新", wx.DefaultPosition, wx.DefaultSize, 0)
        button.Bind(wx.EVT_BUTTON, self.on_refresh)
        sizer.Add(d_tilte, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.lb_devices, 1, wx.EXPAND | wx.ALL, 0)
        sizer.Add(f_title, 0, wx.EXPAND | wx.TOP, 5)
        sizer.Add(self.lb_fastboot, 1, wx.EXPAND | wx.ALL, 0)
        sizer.Add(button, 0, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_upgrade_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"升级"), wx.VERTICAL)
        upgrade_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button = wx.Button(self, wx.ID_ANY, u"升级", wx.DefaultPosition, (50, -1), 0)
        button.Bind(wx.EVT_BUTTON, self.on_upgrade)
        self.fpc = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"选择升级配置文件",
                                     u"*.cfg", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE | wx.FLP_SMALL)
        upgrade_sizer.Add(self.fpc, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        upgrade_sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        sizer.Add(upgrade_sizer, 0, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_upgrade_info_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u""), wx.VERTICAL)
        self.scrolled_window = wx.ScrolledWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                                 wx.HSCROLL | wx.VSCROLL)
        self.scrolled_window.SetScrollRate(5, 5)
        self.scrolled_window.Layout()
        sizer.Fit(self.scrolled_window)
        sizer.Add(self.scrolled_window, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def on_refresh(self, event):
        self.lb_devices.Set(["Refreshing"])
        self.lb_fastboot.Set(["Refreshing"])
        Utility.append_work(target=self.__refresh, allow_dupl=False)

    def __refresh(self):
        self.lb_devices.Set(Utility.get_devices())
        self.lb_fastboot.Set(Utility.get_fastboots())

    def on_upgrade(self, event):
        config_path = self.fpc.GetPath()
        if not config_path or not os.path.exists(config_path):
            self.alert_error(u"没有找到升级配置文件，请确认。")
            return False
        if not self.check_upgrade_list():
            self.alert_error(u"还有设备正在升级中，请稍等。")
            return False
        self.upgrade_list = list()
        self.scrolled_window.DestroyChildren()
        sizer = wx.BoxSizer(wx.VERTICAL)
        m_path, m_config = self.parse_config(config_path)
        for device in self.get_selected_devices():
            upgrade = UpgradeDevice(parent=self.scrolled_window, serial=device, _type="device",
                                    config=(m_path, m_config))
            self.upgrade_list.append(upgrade)
            sizer.Add(upgrade.get_sizer(), 0, wx.EXPAND | wx.ALL, 1)
        for fastboot in self.get_selected_fastboot():
            upgrade = UpgradeDevice(parent=self.scrolled_window, serial=fastboot, _type="fastboot",
                                    config=(m_path, m_config))
            self.upgrade_list.append(upgrade)
            sizer.Add(upgrade.get_sizer(), 0, wx.EXPAND | wx.ALL, 1)
        self.scrolled_window.SetSizer(sizer)
        self.upgrade_info_sizer.Layout()
        self.scrolled_window.Scroll(0, 0)
        for need_upgrade in self.upgrade_list:
            need_upgrade.start()

    def check_upgrade_list(self):
        for uprader in self.upgrade_list:
            if uprader.is_alive():
                return False
        return True

    def get_selected_devices(self):
        lst = list()
        items = self.lb_devices.GetItems()
        for i in self.lb_devices.GetSelections():
            lst.append(items[i])
        return lst

    def get_selected_fastboot(self):
        lst = list()
        items = self.lb_fastboot.GetItems()
        for i in self.lb_fastboot.GetSelections():
            lst.append(items[i])
        return lst

    def alert_error(self, msg):
        dlg = wx.MessageDialog(self, msg, u"错误", style=wx.ICON_ERROR | wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def parse_config(self, config_path):
        p = os.path.dirname(config_path)
        lst = list()
        with open(config_path) as f:
            for line in f.readlines():
                line = line.strip('\r\n')
                if not line:
                    continue
                lst.append(re.split(r"\s+", line))
        return p, lst

    def ready_to_close(self):
        return self.check_upgrade_list()


class UpgradeDevice(object):
    def __init__(self, parent, serial, _type, config):
        self.type = _type
        self.serial = serial
        self.m_path, self.m_config = config
        self.progress_count = len(self.m_config)
        self.font = wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel = wx.Panel(parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.panel.SetBackgroundColour("#CAFCFA")
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        info_sizer = self.__init_info_sizer(serial=serial)
        gauge = self.__init_gauge()
        main_sizer.Add(info_sizer, 0, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(gauge, 0, wx.EXPAND | wx.ALL, 0)
        self.panel.SetSizer(main_sizer)
        self.panel.Layout()
        main_sizer.Fit(self.panel)
        self.sizer.Add(self.panel, 1, wx.EXPAND | wx.ALL, 0)

    def __init_info_sizer(self, serial):
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(self.panel, wx.ID_ANY, serial, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_BOTTOM)
        text.SetFont(self.font)
        self.info_output = wx.StaticText(self.panel, wx.ID_ANY, serial, wx.DefaultPosition, wx.DefaultSize, 0)
        sizer.Add(text, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.info_output, 1, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_gauge(self):
        self.upgarde_gauge = wx.Gauge(self.panel, wx.ID_ANY, self.progress_count, wx.DefaultPosition, wx.DefaultSize,
                                      wx.GA_HORIZONTAL)
        self.upgarde_gauge.SetValue(0)
        return self.upgarde_gauge

    def get_sizer(self):
        return self.sizer

    def start(self):
        Utility.append_work(target=self.__upgrade, allow_dupl=False, thread_name="Upgrade:%s" % self.serial)

    def __upgrade(self):
        if not self.check_file():
            return False
        self.reboot_to_fastboot()
        if self.flash_image_files():
            self.reboot_to_normal()
        else:
            pass

    def flash_image_files(self):
        count = 0
        for config in self.m_config:
            image = config[0]
            partition = config[1]
            if not self.erase(partition=partition):
                return False
            if not self.flash(partition=partition, image=image):
                return False
            count += 1
            self.upgarde_gauge.SetValue(count)
        self.output(u"升级完成，重启中。")
        return True

    def erase(self, partition):
        self.output(u"正在擦除 \"%s\" ..." % partition)
        stdin, stdout, stderr = self.run_command(fastboot.erase(partition=partition, serial=self.serial))
        return self.judge_result(partition=partition, output=stderr.read())

    def flash(self, partition, image):
        self.output(u"正在将文件 \"%s\" 写入到 \"%s\"" % (image, partition))
        image = os.path.join(self.m_path, image)
        stdin, stdout, stderr = self.run_command(fastboot.flash(partition=partition, image=image, serial=self.serial))
        return self.judge_result(partition=partition, output=stderr.read())

    def judge_result(self, partition, output):
        print repr(output)
        if 'OKAY' in output and "FAILED" not in output:
            return True
        else:
            if partition in ['PrimaryGPT', 'BackupGPT']:
                return True
            self.output(u"失败：%s" % repr(output))
            return False

    def reboot_to_fastboot(self):
        if self.type == "device":
            self.run_command(adb.reboot(serial=self.serial, mode='bootloader'))
            time.sleep(3)
            self.run_command(fastboot.wait_for_device(serial=self.serial))

    def reboot_to_normal(self):
        self.run_command(fastboot.reboot(serial=self.serial))

    def check_file(self):
        for config in self.m_config:
            f = os.path.join(self.m_path, config[0])
            self.output(u"正在检查文件：%s" % f)
            if not os.path.exists(f):
                self.output(u"文件不存在：%s,停止升级。" % f)
                return False
        return True

    def is_alive(self):
        return Utility.is_alive("Upgrade:%s" % self.serial)

    def run_command(self, cmd):
        log.info(u"Run Command:%s" % cmd)
        return os.popen3(cmd)

    def output(self, msg):
        wx.CallAfter(self.info_output.SetLabel, msg)
        time.sleep(0.1)
