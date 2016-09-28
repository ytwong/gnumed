#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.6.8
#

import wx

# begin wxGlade: dependencies
import gettext
# end wxGlade


class wxgExternalCareEAPnl(wx.ScrolledWindow):
	def __init__(self, *args, **kwds):

		from Gnumed.wxpython.gmEMRStructWidgets import cIssueSelectionPhraseWheel
		from Gnumed.wxpython.gmOrganizationWidgets import cOrgUnitPhraseWheel
		from Gnumed.wxpython.gmTextCtrl import cTextCtrl

		# begin wxGlade: wxgExternalCareEAPnl.__init__
		kwds["style"] = wx.BORDER_NONE | wx.TAB_TRAVERSAL
		wx.ScrolledWindow.__init__(self, *args, **kwds)
		self._PRW_issue = cIssueSelectionPhraseWheel(self, wx.ID_ANY, "", style=wx.BORDER_NONE)
		self._PRW_care_location = cOrgUnitPhraseWheel(self, wx.ID_ANY, "", style=wx.BORDER_NONE)
		self._BTN_manage_orgs = wx.Button(self, wx.ID_ANY, _("&Manage"), style=wx.BU_EXACTFIT)
		self._TCTRL_provider = cTextCtrl(self, wx.ID_ANY, "", style=wx.BORDER_NONE)
		self._TCTRL_comment = cTextCtrl(self, wx.ID_ANY, "", style=wx.BORDER_NONE)
		self._CHBOX_inactive = wx.CheckBox(self, wx.ID_ANY, _("&Inactive"), style=wx.CHK_2STATE)

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self._on_manage_orgs_button_pressed, self._BTN_manage_orgs)
		# end wxGlade

	def __set_properties(self):
		# begin wxGlade: wxgExternalCareEAPnl.__set_properties
		self.SetScrollRate(10, 10)
		self._PRW_issue.SetToolTipString(_("Mandatory: Select a health issue or enter a new reason for which care is rendered."))
		self._PRW_care_location.SetToolTipString(_("Mandatory: The location care is rendered at."))
		self._BTN_manage_orgs.SetToolTipString(_("Manage organizations and units thereof."))
		self._TCTRL_provider.SetToolTipString(_("Optional: A specific, named provider rendering care at the care location."))
		self._TCTRL_comment.SetToolTipString(_("Optional: A comment on this external care relationship."))
		self._CHBOX_inactive.SetToolTipString(_("Check this if the external care entry is inactive (IOW, historic)."))
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: wxgExternalCareEAPnl.__do_layout
		_gszr_main = wx.FlexGridSizer(5, 2, 1, 3)
		__szr_location_details = wx.BoxSizer(wx.HORIZONTAL)
		__lbl_issue = wx.StaticText(self, wx.ID_ANY, _("Reason"))
		__lbl_issue.SetForegroundColour(wx.Colour(255, 0, 0))
		_gszr_main.Add(__lbl_issue, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		_gszr_main.Add(self._PRW_issue, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		__lbl_org_unit = wx.StaticText(self, wx.ID_ANY, _("Location"))
		__lbl_org_unit.SetForegroundColour(wx.Colour(255, 0, 0))
		_gszr_main.Add(__lbl_org_unit, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		__szr_location_details.Add(self._PRW_care_location, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.RIGHT, 3)
		__szr_location_details.Add(self._BTN_manage_orgs, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		_gszr_main.Add(__szr_location_details, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		__lbl_provider = wx.StaticText(self, wx.ID_ANY, _("Provider"))
		_gszr_main.Add(__lbl_provider, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		_gszr_main.Add(self._TCTRL_provider, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		__lbl_comment = wx.StaticText(self, wx.ID_ANY, _("Comment"))
		_gszr_main.Add(__lbl_comment, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		_gszr_main.Add(self._TCTRL_comment, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		_gszr_main.Add((20, 20), 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		_gszr_main.Add(self._CHBOX_inactive, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		self.SetSizer(_gszr_main)
		_gszr_main.Fit(self)
		_gszr_main.AddGrowableCol(1)
		self.Layout()
		# end wxGlade

	def _on_manage_orgs_button_pressed(self, event):  # wxGlade: wxgExternalCareEAPnl.<event_handler>
		print "Event handler '_on_manage_orgs_button_pressed' not implemented!"
		event.Skip()

# end of class wxgExternalCareEAPnl
