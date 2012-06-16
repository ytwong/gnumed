#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade 0.6.3 from "/home/ncq/Projekte/gm-git/gnumed/gnumed/client/wxg/wxgTopPnl.wxg"

import wx

# begin wxGlade: extracode
# end wxGlade



class wxgTopPnl(wx.Panel):
    def __init__(self, *args, **kwds):

        from Gnumed.wxpython.gmPatPicWidgets import cPatientPicture
        from Gnumed.wxpython.gmPatSearchWidgets import cActivePatientSelector
        from Gnumed.wxpython.gmDemographicsWidgets import cImageTagPresenterPnl
        from Gnumed.wxpython.gmEMRStructWidgets import cActiveEncounterPnl

        # begin wxGlade: wxgTopPnl.__init__
        kwds["style"] = wx.RAISED_BORDER
        wx.Panel.__init__(self, *args, **kwds)
        self._BMP_patient_picture = cPatientPicture(self, -1, wx.NullBitmap)
        self._TCTRL_patient_selector = cActivePatientSelector(self, -1, "")
        self._LBL_age = wx.StaticText(self, -1, _("<age>"))
        self._LBL_allergies = wx.StaticText(self, -1, _("Caveat"))
        self._TCTRL_allergies = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY)
        self._PNL_tags = cImageTagPresenterPnl(self, -1, style=wx.NO_BORDER)
        self._PNL_enc = cActiveEncounterPnl(self, -1, style=wx.SIMPLE_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: wxgTopPnl.__set_properties
        self._BMP_patient_picture.SetMinSize((50, 54))
        self._TCTRL_patient_selector.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, 0, ""))
        self._LBL_age.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, 0, ""))
        self._LBL_age.SetToolTipString(_("The age."))
        self._LBL_allergies.SetForegroundColour(wx.Colour(255, 0, 0))
        self._LBL_allergies.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, 0, ""))
        self._TCTRL_allergies.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BACKGROUND))
        self._TCTRL_allergies.SetForegroundColour(wx.Colour(255, 0, 0))
        self._TCTRL_allergies.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, 0, ""))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: wxgTopPnl.__do_layout
        __szr_main = wx.BoxSizer(wx.HORIZONTAL)
        __szr_stacked_rows = wx.BoxSizer(wx.VERTICAL)
        __szr_bottom_row = wx.BoxSizer(wx.HORIZONTAL)
        __szr_top_row = wx.BoxSizer(wx.HORIZONTAL)
        __szr_main.Add(self._BMP_patient_picture, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 2)
        __szr_top_row.Add(self._TCTRL_patient_selector, 2, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
        __szr_top_row.Add(self._LBL_age, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        __szr_top_row.Add(self._LBL_allergies, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 2)
        __szr_top_row.Add(self._TCTRL_allergies, 3, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_stacked_rows.Add(__szr_top_row, 0, wx.BOTTOM | wx.EXPAND, 2)
        __szr_bottom_row.Add(self._PNL_tags, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_bottom_row.Add((20, 20), 1, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_bottom_row.Add(self._PNL_enc, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_stacked_rows.Add(__szr_bottom_row, 0, wx.EXPAND, 0)
        __szr_main.Add(__szr_stacked_rows, 1, 0, 0)
        self.SetSizer(__szr_main)
        __szr_main.Fit(self)
        # end wxGlade

# end of class wxgTopPnl


