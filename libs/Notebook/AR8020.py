# -*- encoding:UTF-8 -*-
import sys
import wx
import libs.ADB_Command as Adb
import os
import logging
from libs import Utility
import time
import re
import threading
import subprocess

# pattern = re.compile(r'currtnt frame = (\d+)-----total frame = (\d+)\r\n')
pattern = re.compile(r'progress : (\d+) / (\d+)\r\n')

log = logging.getLogger(__name__)


def check_device(level):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print level
            return func(*args)

        return wrapper

    return decorator


class AR8020(wx.Panel):
    def __init__(self, parent):
        self.name = "AR8020"
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)
        MainSizer = wx.BoxSizer(wx.HORIZONTAL)
        LeftSizer = wx.BoxSizer(wx.VERTICAL)
        RightSizer = wx.BoxSizer(wx.VERTICAL)
        devices_sizer = self.__init_devices_sizer()
        state_sizer = self.__init_state_sizer()
        upgrade_sizer = self.__init_upgrade_sizer()
        log_sizer = self.__init_log_sizer()
        LeftSizer.Add(devices_sizer, 1, wx.EXPAND | wx.ALL, 0)
        RightSizer.Add(state_sizer, 0, wx.EXPAND | wx.ALL, 0)
        RightSizer.Add(upgrade_sizer, 0, wx.EXPAND | wx.ALL, 0)
        RightSizer.Add(log_sizer, 1, wx.EXPAND | wx.ALL, 0)
        MainSizer.Add(LeftSizer, 1, wx.EXPAND | wx.ALL, 1)
        MainSizer.Add(RightSizer, 3, wx.EXPAND | wx.ALL, 1)
        self.uart_log = None
        self.SetSizer(MainSizer)
        self.Layout()

    def __init_devices_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"设备"), wx.VERTICAL)
        choices = Utility.get_devices()
        self.lb_devices = wx.ListBox(sizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                     choices, 0)
        self.lb_devices.Bind(wx.EVT_LISTBOX, self.on_select_item)
        button = wx.Button(sizer.GetStaticBox(), wx.ID_ANY, u"刷新", wx.DefaultPosition, wx.DefaultSize, 0)
        button.Bind(wx.EVT_BUTTON, self.on_refresh)
        sizer.Add(self.lb_devices, 1, wx.EXPAND | wx.ALL, 0)
        sizer.Add(button, 0, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_state_sizer(self):
        font = wx.Font(30, wx.MODERN, wx.NORMAL, wx.BOLD)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.state_st = wx.StaticText(self, wx.ID_ANY, u"请选择", wx.DefaultPosition, (-1, -1),
                                      wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        m_open = wx.Button(self, wx.ID_ANY, u"打开", wx.DefaultPosition, wx.DefaultSize, 0)
        m_close = wx.Button(self, wx.ID_ANY, u"关闭", wx.DefaultPosition, wx.DefaultSize, 0)
        m_open.Bind(wx.EVT_BUTTON, self.on_open)
        m_close.Bind(wx.EVT_BUTTON, self.on_close)
        button_sizer.Add(m_open, 0, wx.RIGHT, 3)
        button_sizer.Add(m_close, 0, wx.RIGHT, 3)
        self.state_st.SetFont(font)
        self.state_st.SetBackgroundColour('#8CFAF2')
        sizer.Add(self.state_st, 1, wx.EXPAND | wx.LEFT | wx.TOP, 8)
        sizer.Add(button_sizer, 0, wx.EXPAND | wx.LEFT | wx.TOP, 8)
        return sizer

    def __init_upgrade_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"升级"), wx.VERTICAL)
        upgrade_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.upgarde_gauge = wx.Gauge(self, wx.ID_ANY, 1000, wx.DefaultPosition, wx.DefaultSize,
                                      wx.GA_HORIZONTAL)
        self.upgarde_gauge.SetValue(0)
        self.upgrade_button = wx.Button(self, wx.ID_ANY, u"升级", wx.DefaultPosition, wx.DefaultSize, 0)
        self.upgrade_button.Bind(wx.EVT_BUTTON, self.on_upgrade)
        upgrade_sizer.Add(self.upgarde_gauge, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
        upgrade_sizer.Add(self.upgrade_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        self.fpc = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"选择升级文件",
                                     u"*.bin", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE | wx.FLP_SMALL)
        sizer.Add(self.fpc, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(upgrade_sizer, 0, wx.EXPAND | wx.ALL, 0)
        return sizer

    def __init_log_sizer(self):
        def init_button_sizer():
            button_sizer = wx.BoxSizer(wx.VERTICAL)
            connect = wx.Button(self, wx.ID_ANY, u"连接", wx.DefaultPosition, wx.DefaultSize, 0)
            disconnect = wx.Button(self, wx.ID_ANY, u"断开", wx.DefaultPosition, wx.DefaultSize, 0)
            save = wx.Button(self, wx.ID_ANY, u"保存", wx.DefaultPosition, wx.DefaultSize, 0)
            clear = wx.Button(self, wx.ID_ANY, u"清空", wx.DefaultPosition, wx.DefaultSize, 0)
            chipid = wx.Button(self, wx.ID_ANY, u"ChipID", wx.DefaultPosition, wx.DefaultSize, 0)
            linkid = wx.Button(self, wx.ID_ANY, u"LinkID", wx.DefaultPosition, wx.DefaultSize, 0)
            sn = wx.Button(self, wx.ID_ANY, u"SN", wx.DefaultPosition, wx.DefaultSize, 0)
            uid = wx.Button(self, wx.ID_ANY, u"UID", wx.DefaultPosition, wx.DefaultSize, 0)
            rc = wx.Button(self, wx.ID_ANY, u"RC Info", wx.DefaultPosition, wx.DefaultSize, 0)
            save.Bind(wx.EVT_BUTTON, self.on_save)
            clear.Bind(wx.EVT_BUTTON, self.on_clear)
            connect.Bind(wx.EVT_BUTTON, self.on_connect)
            disconnect.Bind(wx.EVT_BUTTON, self.on_disconnect)
            chipid.Bind(wx.EVT_BUTTON, self.on_chip_id)
            linkid.Bind(wx.EVT_BUTTON, self.on_link_id)
            sn.Bind(wx.EVT_BUTTON, self.on_sn)
            uid.Bind(wx.EVT_BUTTON, self.on_uid)
            rc.Bind(wx.EVT_BUTTON, self.get_rc_info)
            button_sizer.Add(connect, 0, wx.ALL, 0)
            button_sizer.Add(disconnect, 0, wx.ALL, 0)
            button_sizer.Add(save, 0, wx.ALL, 0)
            button_sizer.Add(clear, 0, wx.ALL, 0)
            button_sizer.Add(chipid, 0, wx.TOP, 10)
            button_sizer.Add(linkid, 0, wx.ALL, 0)
            button_sizer.Add(sn, 0, wx.ALL, 0)
            button_sizer.Add(uid, 0, wx.ALL, 0)
            button_sizer.Add(rc, 0, wx.ALL, 0)
            return button_sizer

        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"日志"), wx.HORIZONTAL)
        m_button_sizer = init_button_sizer()
        self.output_tc = wx.TextCtrl(self, -1, '', style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.output_tc.SetInsertionPointEnd()
        sizer.Add(self.output_tc, 1, wx.EXPAND | wx.ALL, 0)
        sizer.Add(m_button_sizer, 0, wx.EXPAND | wx.LEFT, 5)
        return sizer

    def on_save(self, event):
        dlg = wx.FileDialog(
            self,
            message="Save Data:",
            defaultDir=os.getcwd(),
            defaultFile="UartLog_%s.txt" % Utility.get_timestamp(time_fmt="%Y%m%d-%H%M%S"),
            wildcard="Text (*.txt)|*.txt",
            style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            with open(dlg.GetPath(), 'w') as wfile:
                wfile.write(self.output_tc.GetValue())
            return True
        return False

    def on_clear(self, event):
        self.output_tc.Clear()

    def on_open(self, event):
        self.open_ar8020(self.get_device_selection())

    def on_close(self, event):
        self.close_ar8020(self.get_device_selection())

    def __refresh_devices(self):
        devices = Utility.get_devices()
        self.lb_devices.Set(devices)
        if len(devices) == 1:
            self.lb_devices.SetSelection(0)
            self.__update_8020_state()

    def on_refresh(self, event):
        self.lb_devices.Set(["Refreshing"])
        Utility.append_work(target=self.__refresh_devices, allow_dupl=False)

    def on_connect(self, event):
        if self.uart_log and self.uart_log.poll():
            self.uart_log.stop()
        self.uart_log = UartLog(serial=self.get_device_selection(), output=self.output_tc)
        self.uart_log.setDaemon(True)
        self.uart_log.start()

    def on_chip_id(self, event):
        if self.uart_log and self.uart_log.poll():
            dialog = wx.TextEntryDialog(self, u'请输入Chip Id ,格式举例：1 1 1 1 1：', u'NvSetChipId <chip id1~5>:',
                                        style=wx.OK)
            if dialog.ShowModal() == wx.ID_OK:
                value = dialog.GetValue()
                self.uart_log.write('NvSetChipId %s' % value)
            dialog.Destroy()
        else:
            self.alert_error("请先打开uart log。")

    def on_link_id(self, event):
        if self.uart_log and self.uart_log.poll():
            dialog = wx.TextEntryDialog(self, u'请输入Link Id ,格式举例：1 1 1 1 1 0 0：', u'NvSetBbRcId <rc id1~5> <vt id0~1>:',
                                        style=wx.OK)
            if dialog.ShowModal() == wx.ID_OK:
                value = dialog.GetValue()
                self.uart_log.write('NvSetBbRcId %s' % value)
            dialog.Destroy()
        else:
            self.alert_error("请先打开uart log。")

    def on_sn(self, event):
        if self.uart_log and self.uart_log.poll():
            dialog = wx.TextEntryDialog(self, u'请输入SN：', u'setSN',
                                        style=wx.OK)
            if dialog.ShowModal() == wx.ID_OK:
                value = dialog.GetValue()
                self.uart_log.write('setSN %s' % value)
            dialog.Destroy()
        else:
            self.alert_error("请先打开uart log。")

    def on_uid(self, event):
        if self.uart_log and self.uart_log.poll():
            dialog = wx.TextEntryDialog(self, u'请输入UID：', u'setUID 32 byte',
                                        style=wx.OK)
            if dialog.ShowModal() == wx.ID_OK:
                value = dialog.GetValue()
                self.uart_log.write('setUID %s' % value)
            dialog.Destroy()
        else:
            self.alert_error("请先打开uart log。")

    def get_rc_info(self, event):
        if self.uart_log and self.uart_log.poll():
            self.uart_log.write('RC')

    def on_disconnect(self, event):
        self.__disconnect()

    def __disconnect(self):
        if self.uart_log and self.uart_log.poll():
            self.uart_log.stop()
            self.uart_log.stop_exist_uart_log()

    def log_output(self, session):
        pass

    def on_select_item(self, event):
        self.update_8020_state()

    def update_8020_state(self):
        Utility.append_work(target=self.__update_8020_state, allow_dupl=False)

    def __update_8020_state(self):
        state = self.is_ar8020_open(serial=self.lb_devices.GetStringSelection())
        if state == "1\n":
            label = u"已打开"
            bg_color = "#9DFA8C"
        elif state == "0\n":
            label = u"已关闭"
            bg_color = "#C4C4C4"
        else:
            label = u"无法获取状态"
            bg_color = "#F71111"
        self.state_st.SetLabel(label)
        self.state_st.SetBackgroundColour(bg_color)
        self.state_st.Refresh()

    def __upgrade(self):
        bin_file = self.fpc.GetPath()
        if bin_file and os.path.exists(bin_file):
            self.lb_devices.Disable()
            self.upgrade_button.Disable()
            log.debug("Find AR8020 Upgrade File:%s" % bin_file)
            device = self.get_device_selection()
            Utility.run_cmd(Adb.push(local=bin_file, remote="/data/local/tmp/8020.bin", serial=device))
            self.open_ar8020(serial=device)
            p = subprocess.Popen(Adb.shell_command(cmd="upgrade_ar8020 /data/local/tmp/8020.bin", serial=device),
                                 stdout=subprocess.PIPE)
            try:
                while True:
                    data = p.stdout.readline()  # block/wait
                    log.debug(repr(data))
                    if "progress" in data:
                        cur, total = Utility.find_in_string(pattern=pattern, string=data)
                        cur, total = float(cur), int(total)
                        self.upgarde_gauge.SetValue(cur / total * 1000)
                        self.state_st.SetLabel(u"升级中...")
                        time.sleep(0.01)
                        continue
                    elif "get version err" in data:
                        self.alert_error("Get Version Error")
                        break
                    elif "upgrade successed" in data:
                        self.state_st.SetLabel(u"升级完成，正在重启。")
                        self.close_ar8020(serial=device)
                        time.sleep(1)
                        self.open_ar8020(serial=device)
                        break
            except Exception, e:
                self.state_st.SetLabel(u"升级失败")
                self.alert_error('{error}\n{data}'.format(error=e.message, data=repr(data)))
            finally:
                self.lb_devices.Enable()
                self.upgrade_button.Enable()
                p.kill()
        else:
            self.alert_error(u"没有找到升级文件。")

    def on_upgrade(self, event):
        Utility.append_work(target=self.__upgrade, allow_dupl=False)

    def get_device_selection(self):
        return self.lb_devices.GetStringSelection()

    def open_ar8020(self, serial):
        self.__switch_on_off_ar8020(serial=serial, on=True)
        self.update_8020_state()

    def close_ar8020(self, serial):
        self.__switch_on_off_ar8020(serial=serial, on=False)
        self.update_8020_state()

    @staticmethod
    def is_ar8020_open(serial):
        log.debug("check the AR 8020 state in device:%s" % serial)
        stdin, stdout, stderr = Utility.run_cmd(
            Adb.shell_command(cmd="cat /sys/bus/platform/drivers/artosyn_ar8020/soc:ar8020/enable", serial=serial))
        return stdout.read()

    @staticmethod
    def __switch_on_off_ar8020(serial, on):
        state = '1' if on else '0'
        cmd = "echo %s > /sys/bus/platform/drivers/artosyn_ar8020/soc:ar8020/enable" % state
        Utility.run_cmd(Adb.shell_command(cmd=cmd, serial=serial))

    def alert_error(self, msg):
        dlg = wx.MessageDialog(self, msg, u"错误", style=wx.ICON_ERROR | wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def run_cmd(self, cmd):
        log.info(u"Run Command:%s" % cmd)
        return os.popen3(cmd)


class UartLog(threading.Thread):
    def __init__(self, serial, output):
        threading.Thread.__init__(self)
        self.stop_flag = False
        self.serial = serial
        self.output = output
        self.input = list()
        self.session = None

    def run(self):
        self.stop_exist_uart_log()
        self.start_uart_log()
        self.clear_uart_log()

    def stop(self):
        self.stop_flag = True

    def write(self, command):
        command = command.strip('\r\n') + '\n'
        self.session.stdin.write(command)
        self.session.stdin.flush()

    def poll(self):
        if self.session:
            if self.session.poll() is None:
                return True
        return False

    def get_serial(self):
        return self.serial

    def stop_exist_uart_log(self):
        self.stop_background_uart_log(self.serial)
        output = os.popen(Adb.shell_command(cmd="ps -A |grep uart_log", serial=self.serial)).read()
        for line in output.split('\n'):
            if not line:
                continue
            pid = Utility.find_in_string(re.compile(r'\d+'), line)
            log.info("%s\t>\tpid:%s" % (line, pid))
            Utility.run_cmd(Adb.shell_command(cmd='kill -2 %s' % pid, serial=self.serial))

    def start_uart_log(self):
        self.session = subprocess.Popen(Adb.shell_command(cmd='uart_log', serial=self.serial), stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        wx.CallAfter(self.output.AppendText, u"已开启设备：<%s>的UART LOG\n" % self.serial)
        while True:
            if self.stop_flag:
                break
            if self.session.poll() == 0:
                break
            line = self.session.stdout.readline().strip('\r\n')
            if line:
                wx.CallAfter(self.output.AppendText,
                             '{time} :  {line}\n'.format(time=Utility.get_timestamp("%H_%M_%S"), line=line))
        wx.CallAfter(self.output.AppendText, u"已关闭设备：<%s>的UART LOG\n" % self.serial)

    def clear_uart_log(self):
        self.session.kill()
        self.session.terminate()

    @staticmethod
    def stop_background_uart_log(serial):
        Utility.run_cmd(Adb.shell_command(cmd="stop uart_log", serial=serial))


if __name__ == '__main__':
    log = UartLog(serial='8f69c4ae', output=None)
    log.start()
    import time

    for x in range(1000):
        time.sleep(0.5)
        if x % 30 == 1:
            log.write('help')
