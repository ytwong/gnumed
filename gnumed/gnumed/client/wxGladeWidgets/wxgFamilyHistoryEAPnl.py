#!/usr/bin/env python
# -*- coding: utf8 -*-
# generated by wxGlade 0.6.3 from "/home/ncq/Projekte/gm-git/gnumed/gnumed/client/wxg/wxgFamilyHistoryEAPnl"

import wx

# begin wxGlade: extracode
# end wxGlade



class wxgFamilyHistoryEAPnl(wx.ScrolledWindow):
    def __init__(self, *args, **kwds):

        #from Gnumed.wxpython.gmFamilyHistoryWidgets import cFamilyHistoryRelationType
        from Gnumed.wxpython.gmEMRStructWidgets import cEpisodeSelectionPhraseWheel
        from Gnumed.wxpython.gmDateTimeInput import cIntervalPhraseWheel
        from Gnumed.wxpython.gmDateTimeInput import cDateInputPhraseWheel
        from Gnumed.wxpython.gmGuiHelpers import cThreeValuedLogicPhraseWheel
        from Gnumed.wxpython.gmPhraseWheel import cPhraseWheel
        from Gnumed.wxpython.gmFamilyHistoryWidgets import cRelationshipTypePhraseWheel

        # begin wxGlade: wxgFamilyHistoryEAPnl.__init__
        kwds["style"] = wx.NO_BORDER|wx.TAB_TRAVERSAL
        wx.ScrolledWindow.__init__(self, *args, **kwds)
        self._PRW_relationship = cRelationshipTypePhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._PRW_condition = cPhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._TCTRL_age_of_onset = wx.TextCtrl(self, -1, "", style=wx.NO_BORDER)
        self._PRW_died_of_this = cThreeValuedLogicPhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._PRW_age_of_death = cIntervalPhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._PRW_episode = cEpisodeSelectionPhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._TCTRL_name = wx.TextCtrl(self, -1, "", style=wx.NO_BORDER)
        self._PRW_dob = cDateInputPhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._TCTRL_comment = wx.TextCtrl(self, -1, "", style=wx.NO_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: wxgFamilyHistoryEAPnl.__set_properties
        self.SetScrollRate(10, 10)
        self._PRW_relationship.SetToolTipString(_("Required: Enter or select the type of relationship between the patient and this relative."))
        self._PRW_condition.SetToolTipString(_("Required: Enter or select the name of the condition the relative suffered from."))
        self._TCTRL_age_of_onset.SetToolTipString(_("Optional: Age of onset of the condition in the relative."))
        self._PRW_died_of_this.SetToolTipString(_("Optional: Whether this condition contributed to the death of the patient."))
        self._PRW_age_of_death.SetToolTipString(_("Optional: Enter the age of death of the relative."))
        self._PRW_episode.SetToolTipString(_("Optional: The episode under which this family history item became known or to which it is relevant.\n\nIf blank: Will be added to an unattributed episode \"Family History\"."))
        self._TCTRL_name.SetToolTipString(_("Optional: Enter the name of the relative."))
        self._PRW_dob.SetToolTipString(_("Optional: Enter the date of birth of the relative."))
        self._TCTRL_comment.SetToolTipString(_("Optional: A comment on this family history item."))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: wxgFamilyHistoryEAPnl.__do_layout
        _gszr_main = wx.FlexGridSizer(7, 2, 1, 3)
        __szr_relation = wx.BoxSizer(wx.HORIZONTAL)
        __szr_death = wx.BoxSizer(wx.HORIZONTAL)
        __szr_condition_details = wx.BoxSizer(wx.HORIZONTAL)
        __lbl_relation = wx.StaticText(self, -1, _("Relationship"))
        __lbl_relation.SetForegroundColour(wx.Colour(255, 0, 0))
        _gszr_main.Add(__lbl_relation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        _gszr_main.Add(self._PRW_relationship, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        __lbl_condition = wx.StaticText(self, -1, _("Condition"))
        __lbl_condition.SetForegroundColour(wx.Colour(255, 0, 0))
        _gszr_main.Add(__lbl_condition, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        _gszr_main.Add(self._PRW_condition, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __lbl_condition_details = wx.StaticText(self, -1, _("Age onset"))
        _gszr_main.Add(__lbl_condition_details, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_condition_details.Add(self._TCTRL_age_of_onset, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        _gszr_main.Add(__szr_condition_details, 1, wx.EXPAND, 0)
        __lbl_died_of_this = wx.StaticText(self, -1, _("Caused death ?"))
        _gszr_main.Add(__lbl_died_of_this, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        __szr_death.Add(self._PRW_died_of_this, 0, wx.RIGHT|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        __lbl_death = wx.StaticText(self, -1, _("Age of death:"))
        __szr_death.Add(__lbl_death, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 3)
        __szr_death.Add(self._PRW_age_of_death, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        _gszr_main.Add(__szr_death, 1, wx.EXPAND, 0)
        __lbl_episode = wx.StaticText(self, -1, _("Episode"))
        __lbl_episode.SetForegroundColour(wx.Colour(255, 127, 0))
        _gszr_main.Add(__lbl_episode, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        _gszr_main.Add(self._PRW_episode, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __lbl_name = wx.StaticText(self, -1, _("Person's name"))
        _gszr_main.Add(__lbl_name, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_relation.Add(self._TCTRL_name, 1, wx.RIGHT|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        __lbl_dob = wx.StaticText(self, -1, _("Date of birth:"))
        __szr_relation.Add(__lbl_dob, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 3)
        __szr_relation.Add(self._PRW_dob, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        _gszr_main.Add(__szr_relation, 1, wx.EXPAND, 0)
        __lbl_comment = wx.StaticText(self, -1, _("Comment"))
        _gszr_main.Add(__lbl_comment, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        _gszr_main.Add(self._TCTRL_comment, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        self.SetSizer(_gszr_main)
        _gszr_main.Fit(self)
        _gszr_main.AddGrowableCol(1)
        # end wxGlade

# end of class wxgFamilyHistoryEAPnl


