#!/usr/bin/env python
# -*- coding: utf8 -*-
# generated by wxGlade 0.6.3 from "/home/ncq/Projekte/gm-git/gnumed/gnumed/client/wxg/wxgVaccineEAPnl.wxg"

import wx

# begin wxGlade: extracode
# end wxGlade



class wxgVaccineEAPnl(wx.ScrolledWindow):
    def __init__(self, *args, **kwds):

        from Gnumed.wxpython import gmMedicationWidgets
        from Gnumed.wxpython import gmPhraseWheel
        from Gnumed.wxpython.gmVaccWidgets import cVaccinationIndicationsPnl

        # begin wxGlade: wxgVaccineEAPnl.__init__
        kwds["style"] = wx.NO_BORDER|wx.TAB_TRAVERSAL
        wx.ScrolledWindow.__init__(self, *args, **kwds)
        self._PRW_brand = gmMedicationWidgets.cBrandedDrugPhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._PRW_route = gmPhraseWheel.cPhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._CHBOX_live = wx.CheckBox(self, -1, _("Live"))
        self._CHBOX_fake = wx.CheckBox(self, -1, _("Fake"))
        self._PNL_indications = cVaccinationIndicationsPnl(self, -1, style=wx.NO_BORDER|wx.TAB_TRAVERSAL)
        self._PRW_atc = gmMedicationWidgets.cATCPhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._PRW_age_min = gmPhraseWheel.cPhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._PRW_age_max = gmPhraseWheel.cPhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._TCTRL_comment = wx.TextCtrl(self, -1, "", style=wx.NO_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: wxgVaccineEAPnl.__set_properties
        self.SetScrollRate(10, 10)
        self._PRW_route.SetToolTipString(_("The route by which this vaccine is to be administered.\n\nTypically one of i.m., s.c., or orally."))
        self._CHBOX_live.SetToolTipString(_("Check if this is a live attenuated vaccine."))
        self._CHBOX_fake.SetToolTipString(_("Whether this is an actual brand or a generic, fake vaccine."))
        self._PRW_atc.SetToolTipString(_("The ATC for this vaccine."))
        self._PRW_age_min.SetToolTipString(_("The minimum age at which this vaccine should be given."))
        self._PRW_age_max.SetToolTipString(_("The maximum age at which this vaccine should be given."))
        self._TCTRL_comment.SetToolTipString(_("Any comment you may wish to relate to this vaccine."))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: wxgVaccineEAPnl.__do_layout
        _gszr_main = wx.FlexGridSizer(6, 2, 1, 3)
        __szr_age_range = wx.BoxSizer(wx.HORIZONTAL)
        _SZR_indications = wx.BoxSizer(wx.VERTICAL)
        __szr_route_details = wx.BoxSizer(wx.HORIZONTAL)
        __lbl_name = wx.StaticText(self, -1, _("Name"))
        __lbl_name.SetForegroundColour(wx.Colour(255, 0, 0))
        _gszr_main.Add(__lbl_name, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        _gszr_main.Add(self._PRW_brand, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __lbl_route = wx.StaticText(self, -1, _("Route"))
        __lbl_route.SetForegroundColour(wx.Colour(255, 0, 0))
        _gszr_main.Add(__lbl_route, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_route_details.Add(self._PRW_route, 1, wx.RIGHT|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        __szr_route_details.Add(self._CHBOX_live, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        __szr_route_details.Add(self._CHBOX_fake, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        _gszr_main.Add(__szr_route_details, 1, wx.EXPAND, 0)
        __lbl_indications = wx.StaticText(self, -1, _("Protects\nfrom"))
        __lbl_indications.SetForegroundColour(wx.Colour(255, 0, 0))
        _gszr_main.Add(__lbl_indications, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        _SZR_indications.Add(self._PNL_indications, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        _gszr_main.Add(_SZR_indications, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __lbl_atc = wx.StaticText(self, -1, _("ATC"))
        _gszr_main.Add(__lbl_atc, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        _gszr_main.Add(self._PRW_atc, 1, wx.EXPAND, 0)
        __lbl_age_range = wx.StaticText(self, -1, _("Age range"))
        _gszr_main.Add(__lbl_age_range, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_age_range.Add(self._PRW_age_min, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __lbl_from_to = wx.StaticText(self, -1, _(u"→"))
        __szr_age_range.Add(__lbl_from_to, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
        __szr_age_range.Add(self._PRW_age_max, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        _gszr_main.Add(__szr_age_range, 1, wx.EXPAND, 0)
        __lbl_comment = wx.StaticText(self, -1, _("Comment"))
        _gszr_main.Add(__lbl_comment, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        _gszr_main.Add(self._TCTRL_comment, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        self.SetSizer(_gszr_main)
        _gszr_main.Fit(self)
        _gszr_main.AddGrowableCol(1)
        # end wxGlade

# end of class wxgVaccineEAPnl


