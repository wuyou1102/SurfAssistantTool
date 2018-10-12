# -*- encoding:UTF-8 -*-
import wx
from libs import Utility
import os
import sys
from libs import ADB_Command as adb
import shutil
from libs.Notebook.Panel import LogcatConfig
import logging
from wx import Image

log = logging.getLogger(__name__)
TMP = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "TMP")
if not os.path.exists(TMP):
    os.makedirs(TMP)

EMPTY_IMAGE = Image(540, 270, True)


class AndroidCatchLog(wx.Panel):
    def __init__(self, parent):
        self.name = u"Android日志"
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour("#EDEDED")
        self.button_default_size = (50, 30)
        MainSizer = wx.BoxSizer(wx.HORIZONTAL)
        LeftSizer = wx.BoxSizer(wx.VERTICAL)
        RightSizer = wx.BoxSizer(wx.VERTICAL)
        RightTopSizer = wx.BoxSizer(wx.HORIZONTAL)

        devices_sizer = self.__init_devices_sizer()
        operation_sizer = self.__init_operation_sizer()
        image_sizer = self.__init_image_sizer()
        self.logcat_config = LogcatConfig(self)
        LeftSizer.Add(devices_sizer, 1, wx.EXPAND | wx.ALL, 0)
        LeftSizer.Add(operation_sizer, 0, wx.EXPAND | wx.TOP, 2)
        RightTopSizer.Add(image_sizer, 0, wx.ALL, 0)
        RightTopSizer.Add(self.logcat_config, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 1)
        RightSizer.Add(RightTopSizer, 1, wx.EXPAND | wx.ALL, 0)

        MainSizer.Add(LeftSizer, 1, wx.EXPAND | wx.ALL, 1)
        MainSizer.Add(RightSizer, 4, wx.EXPAND | wx.ALL, 1)
        self.SetSizer(MainSizer)
        self.Layout()


    def __init_devices_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"设备"), wx.VERTICAL)
        choices = Utility.get_devices()
        self.lb_devices = wx.ListBox(sizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                     choices, 0)
        button = wx.Button(sizer.GetStaticBox(), wx.ID_ANY, u"刷新", wx.DefaultPosition, wx.DefaultSize, 0)
        button.Bind(wx.EVT_BUTTON, self.on_refresh)
        sizer.Add(self.lb_devices, 1, wx.EXPAND | wx.ALL, 0)
        sizer.Add(button, 0, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_operation_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"操作"), wx.VERTICAL)
        row1 = self.__init_row1(sizer.GetStaticBox())
        row2 = self.__init_row2(sizer.GetStaticBox())
        sizer.Add(row1, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(row2, 0, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_row1(self, parent):
        row = wx.BoxSizer(wx.HORIZONTAL)
        button1 = wx.Button(parent, wx.ID_ANY, u"电源键", wx.DefaultPosition, self.button_default_size, 0)
        button2 = wx.Button(parent, wx.ID_ANY, u"ROOT", wx.DefaultPosition, self.button_default_size, 0)
        button1.Bind(wx.EVT_BUTTON, self.on_power)
        button2.Bind(wx.EVT_BUTTON, self.on_root)
        row.Add(button1, 1, wx.EXPAND | wx.ALL, 1)
        row.Add(button2, 1, wx.EXPAND | wx.ALL, 1)
        return row

    def __init_row2(self, parent):
        row = wx.BoxSizer(wx.HORIZONTAL)
        button1 = wx.Button(parent, wx.ID_ANY, u"音量+", wx.DefaultPosition, self.button_default_size, 0)
        button2 = wx.Button(parent, wx.ID_ANY, u"音量-", wx.DefaultPosition, self.button_default_size, 0)
        button1.Bind(wx.EVT_BUTTON, self.on_volume_up)
        button2.Bind(wx.EVT_BUTTON, self.on_volume_down)
        row.Add(button1, 1, wx.EXPAND | wx.ALL, 1)
        row.Add(button2, 1, wx.EXPAND | wx.ALL, 1)
        return row

    def __init_image_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"截图"), wx.VERTICAL)
        self.screenshots1 = Screenshots(parent=self, display_id=1)
        sizer.Add(self.screenshots1, 1, wx.ALIGN_LEFT | wx.ALL, 0)
        self.screenshots0 = Screenshots(parent=self, display_id=0)
        sizer.Add(self.screenshots0, 1, wx.ALIGN_LEFT | wx.TOP, 5)
        return sizer

    def on_refresh(self, event):
        self.lb_devices.Set(["Refreshing"])
        Utility.append_work(target=self.__refresh_devices, allow_dupl=False)

    def __refresh_devices(self):
        devices = Utility.get_devices()
        self.lb_devices.Set(devices)
        if len(devices) == 1:
            self.lb_devices.SetSelection(0)

    def get_device_selection(self):
        return self.lb_devices.GetStringSelection()

    def on_power(self, event):
        device = self.get_device_selection()
        os.popen(adb.shell_command("input keyevent 26", serial=device))

    def on_root(self, event):
        device = self.get_device_selection()
        os.popen(adb.root(serial=device))
        Utility.append_work(target=self.__refresh_devices, allow_dupl=False)

    def on_volume_up(self, event):
        device = self.get_device_selection()
        os.popen(adb.shell_command("input keyevent 24", serial=device))

    def on_volume_down(self, event):
        device = self.get_device_selection()
        os.popen(adb.shell_command("input keyevent 25", serial=device))


class Screenshots(wx.StaticBitmap):
    def __init__(self, parent, display_id):
        wx.StaticBitmap.__init__(self, parent=parent, id=wx.ID_ANY, bitmap=wx.Bitmap(EMPTY_IMAGE), size=(540, 270))
        self.parent = parent
        self.display_id = display_id
        self.image_path = None
        self.Bind(wx.EVT_LEFT_UP, self.refresh_screenshots_ctrl)
        self.Bind(wx.EVT_RIGHT_DCLICK, self.save_screenshots)

    def refresh_screenshots_ctrl(self, event):
        self.SetBitmap(wx.Bitmap(EMPTY_IMAGE))
        Utility.append_work(target=self.set_screenshots, allow_dupl=False,
                            thread_name="set_screenshots_%s" % self.display_id)

    def get_image_path(self):
        return self.image_path

    def set_screenshots(self):
        screenshots_name = "screenshots%s.png" % self.display_id
        save_path = "/data/local/tmp/%s" % screenshots_name
        local_path = os.path.join(TMP, screenshots_name)
        cmd = "screencap -d {id} -p {path}".format(id=self.display_id, path=save_path)
        os.popen(adb.shell_command(cmd=cmd, serial=self.parent.get_device_selection()))
        os.popen(adb.pull(remote=save_path, local=local_path))
        self.image_path = local_path
        self.SetBitmap(self.convert_image())

    def convert_image(self):
        if not os.path.exists(self.image_path):
            return False
        image = Image(self.image_path, wx.BITMAP_TYPE_PNG)
        width = image.GetWidth() / 4
        height = image.GetHeight() / 4
        return image.Scale(width, height).ConvertToBitmap()

    def save_screenshots(self, event):
        if not self.image_path:
            return False
        dlg = wx.FileDialog(
            self,
            message="Save screenshots",
            defaultDir=os.getcwd(),
            defaultFile="Screenshots%s_%s.png" % (self.display_id, Utility.get_timestamp(time_fmt="%Y%m%d-%H%M%S")),
            wildcard="Screenshots (*.png)|*.png",
            style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            save_path = dlg.GetPath()
            shutil.copyfile(self.image_path, save_path)
            return True
        return False
