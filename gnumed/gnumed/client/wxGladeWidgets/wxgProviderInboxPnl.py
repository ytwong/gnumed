#!/usr/bin/env python
# -*- coding: ISO-8859-15 -*-
# generated by wxGlade 0.4cvs on Tue May  9 20:39:48 2006

import wx

class wxgProviderInboxPnl(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: wxgProviderInboxPnl.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self._msg_welcome = wx.StaticText(self, -1, _("Programmer must override this text."), style=wx.ALIGN_CENTRE)
        self._LCTRL_provider_inbox = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.SIMPLE_BORDER)
        self._TXT_inbox_item_comment = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL|wx.TE_LINEWRAP|wx.TE_WORDWRAP)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._lst_item_activated, self._LCTRL_provider_inbox)
        self.Bind(wx.EVT_LIST_ITEM_FOCUSED, self._lst_item_focused, self._LCTRL_provider_inbox)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._lst_item_right_clicked, self._LCTRL_provider_inbox)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: wxgProviderInboxPnl.__set_properties
        self._LCTRL_provider_inbox.SetFocus()
        self._TXT_inbox_item_comment.SetToolTipString(_("This shows the entirety of the selected message in your Inbox."))
        self._TXT_inbox_item_comment.Enable(False)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: wxgProviderInboxPnl.__do_layout
        __szr_main = wx.BoxSizer(wx.VERTICAL)
        __szr_main.Add(self._msg_welcome, 0, wx.ADJUST_MINSIZE, 0)
        __szr_main.Add(self._LCTRL_provider_inbox, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        __szr_main.Add(self._TXT_inbox_item_comment, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        self.SetAutoLayout(True)
        self.SetSizer(__szr_main)
        __szr_main.Fit(self)
        __szr_main.SetSizeHints(self)
        # end wxGlade

    def _lst_item_activated(self, event): # wxGlade: wxgProviderInboxPnl.<event_handler>
        print "Event handler `_lst_item_activated' not implemented!"
        event.Skip()

    def _lst_item_focused(self, event): # wxGlade: wxgProviderInboxPnl.<event_handler>
        print "Event handler `_lst_item_focused' not implemented!"
        event.Skip()

    def _lst_item_right_clicked(self, event): # wxGlade: wxgProviderInboxPnl.<event_handler>
        print "Event handler `_lst_item_right_clicked' not implemented!"
        event.Skip()

# end of class wxgProviderInboxPnl


