# -*- encoding:UTF-8 -*-
import sys
import wx
import Notebook

reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=999, title="Surf Assistant Tool", size=(1024, 768))
        self.Center()
        notebook = wx.Notebook(self)
        self.android_log = Notebook.AndroidCatchLog(parent=notebook)
        self.android_upgrade = Notebook.AndroidUpgrade(parent=notebook)
        self.ar_8020 = Notebook.AR8020(parent=notebook)

        notebook.AddPage(self.android_log, self.android_log.name)
        notebook.AddPage(self.android_upgrade, self.android_upgrade.name)
        notebook.AddPage(self.ar_8020, self.ar_8020.name)

    def alert_error(self, msg):
        dlg = wx.MessageDialog(self, msg, u"错误", style=wx.ICON_ERROR | wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def Destroy(self):
        if self.android_upgrade.ready_to_close():
            return super(Frame, self).Destroy()
        else:
            self.alert_error(u"还有正在升级的程序，请等待升级结束后关闭。")
            return False
