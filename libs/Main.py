# -*- encoding:UTF-8 -*-
import sys
import wx
import Notebook

reload(sys)
sys.setdefaultencoding('utf-8')


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=999, title="Surf Assistant Tool", size=(800, 600))
        self.Center()
        notebook = wx.Notebook(self)
        self.sdm_660 = Notebook.SDM660(parent=notebook)
        self.ar_8020 = Notebook.AR8020(parent=notebook)

        notebook.AddPage(self.sdm_660, self.sdm_660.name)
        notebook.AddPage(self.ar_8020, self.ar_8020.name)

    def alert_error(self, msg):
        dlg = wx.MessageDialog(self, msg, u"错误", style=wx.ICON_ERROR | wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def Destroy(self):
        if self.sdm_660.ready_to_close():
            return super(Frame, self).Destroy()
        else:
            self.alert_error(u"还有正在升级的程序，请等待升级结束后关闭。")
            return False
