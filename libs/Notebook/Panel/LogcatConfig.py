# -*- encoding:UTF-8 -*-
import wx
from libs import Utility
import os
import sys


class LogcatConfig(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                          style=wx.TAB_TRAVERSAL)
        MainSizer = wx.BoxSizer(wx.HORIZONTAL)
        config_sizer = self.__init_logcat_config_sizer()
        MainSizer.Add(config_sizer, 1, wx.EXPAND | wx.ALL, 1)
        self.SetSizer(MainSizer)
        self.Layout()

    def __init_choice(self, title, choices):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_ctrl = wx.StaticText(self, wx.ID_ANY, u"%s：" % title)
        choice_ctrl = wx.Choice(self, wx.ID_ANY, choices=choices)
        choice_ctrl.SetSelection(0)
        sizer.Add(title_ctrl, 2, wx.ALIGN_CENTER | wx.EXPAND | wx.TOP, 4)
        sizer.Add(choice_ctrl, 5, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, 0)
        return sizer, choice_ctrl

    def __init_filter(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        wx_checkbox = wx.CheckBox(self, wx.ID_ANY, u"过滤器")
        wx_checkbox.Bind(wx.EVT_CHECKBOX, self.on_check)
        sizer.Add(wx_checkbox, 0, wx.ALL, 0)

        return sizer, wx_checkbox

    def __init_priority_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, wx.ID_ANY, u":")
        tag = wx.TextCtrl(self, wx.ID_ANY)
        w, h = tag.GetSize()
        plus = wx.Button(self, wx.ID_ANY, u"+", size=(40, h))
        choice_ctrl = wx.Choice(self, wx.ID_ANY,
                                choices=[u"Verbose", u"Debug", u"Info", u"Warning", u"Error", u"Fatal", u"Silent"])
        sizer.Add(tag, 1, wx.ALL, 1)
        sizer.Add(text, 0, wx.LEFT | wx.RIGHT, 5)
        sizer.Add(choice_ctrl, 0, wx.ALL, 1)
        sizer.Add(plus, 0, wx.ALL, 1)
        return sizer

    def __init_logcat_config_sizer(self):
        sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"日志配置"), wx.VERTICAL)
        buff_sizer, self.buff_choice = self.__init_choice(title=u"缓冲区",
                                                          choices=[u"Main", u"System", u"Radio", u"Event"])
        format_sizer, self.format_choice = self.__init_choice(title=u"格式控制",
                                                              choices=[u"Default", u"Brief", u"Process", u"Tag",
                                                                       u"Thread", u"Raw", u"Time", u"Long"])
        filter_sizer, self.filter_checkbox = self.__init_filter()
        priority_sizer = self.__init_priority_sizer()

        sizer.Add(buff_sizer, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(format_sizer, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(filter_sizer, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(priority_sizer, 0, wx.EXPAND | wx.ALL, 2)
        return sizer

    def on_check(self, event):
        pass
