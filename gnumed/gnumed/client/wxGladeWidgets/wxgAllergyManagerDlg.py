#!/usr/bin/env python
# -*- coding: ISO-8859-15 -*-
# generated by wxGlade 0.4.1 on Thu Mar 15 15:07:14 2007

import wx

class wxgAllergyManagerDlg(wx.Dialog):
    def __init__(self, *args, **kwds):

        from Gnumed.wxpython import gmListWidgets, gmAllergyWidgets

        # begin wxGlade: wxgAllergyManagerDlg.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self._TXT_current_state = wx.StaticText(self, -1, _("<current allergy state>"))
        self._TXT_last_confirmed = wx.StaticText(self, -1, _("<last confirmed>"))
        self._RBTN_unknown = wx.RadioButton(self, -1, _("Unknown"))
        self._RBTN_none = wx.RadioButton(self, -1, _("No known allergies"))
        self._RBTN_some = wx.RadioButton(self, -1, _("Has allergies"))
        self._TCTRL_state_comment = wx.TextCtrl(self, -1, "", style=wx.NO_BORDER)
        self._BTN_confirm = wx.Button(self, -1, _("&Update / Con&firm"))
        self.__szr_state_staticbox = wx.StaticBox(self, -1, _("Allergy state"))
        self._LCTRL_allergies = gmListWidgets.cReportListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.NO_BORDER)
        self._LBL_message = wx.StaticText(self, -1, _("Input new allergy, or select from among existing allergy items to edit them:"))
        self._PNL_edit_area = gmAllergyWidgets.cAllergyEditAreaPnl(self, -1, style=wx.NO_BORDER | wx.TAB_TRAVERSAL)
        self._BTN_save_details = wx.Button(self, wx.ID_SAVE, "", style=wx.BU_EXACTFIT)
        self._BTN_clear = wx.Button(self, wx.ID_CLEAR, "", style=wx.BU_EXACTFIT)
        self._BTN_delete = wx.Button(self, wx.ID_DELETE, "", style=wx.BU_EXACTFIT)
        self.__szr_details_staticbox = wx.StaticBox(self, -1, _("Allergy details"))
        self.__hline_bottom = wx.StaticLine(self, -1)
        self._BTN_dismiss = wx.Button(self, wx.ID_CLOSE, "")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self._on_confirm_button_pressed, self._BTN_confirm)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_list_item_selected, self._LCTRL_allergies)
        self.Bind(wx.EVT_BUTTON, self._on_save_details_button_pressed, self._BTN_save_details)
        self.Bind(wx.EVT_BUTTON, self._on_clear_button_pressed, self._BTN_clear)
        self.Bind(wx.EVT_BUTTON, self._on_delete_button_pressed, self._BTN_delete)
        self.Bind(wx.EVT_BUTTON, self._on_dismiss_button_pressed, self._BTN_dismiss)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: wxgAllergyManagerDlg.__set_properties
        self.SetTitle(_("Allergy Manager"))
        self.SetSize((650, 500))
        self._TXT_current_state.SetToolTipString(_("This displays the current allergy state as saved in the database."))
        self._TXT_last_confirmed.SetToolTipString(_("When was the allergy state last confirmed."))
        self._RBTN_unknown.SetToolTipString(_("Select this if there is no information available on whether the patient has any allergies or not."))
        self._RBTN_none.SetToolTipString(_("Select this if the patient has no known allergies."))
        self._RBTN_some.SetToolTipString(_("Select this if the patient has known allergies."))
        self._TCTRL_state_comment.SetToolTipString(_("A comment on the allergy state."))
        self._BTN_confirm.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self._BTN_confirm.SetToolTipString(_("Save and confirm the allergy state."))
        self._LCTRL_allergies.SetToolTipString(_("Lists the allergies known for this patient if any."))
        self._BTN_save_details.SetToolTipString(_("Save the allergy details in the edit area as either a new allergy or as an update to the existing allergy selected above."))
        self._BTN_clear.SetToolTipString(_("Clear the fields of the edit area. Will discard unsaved data."))
        self._BTN_delete.SetToolTipString(_("Delete the allergy selected in the list from the database."))
        self._BTN_delete.Enable(False)
        self._BTN_dismiss.SetToolTipString(_("Close the dialag. Will discard unsaved data."))
        self._BTN_dismiss.SetDefault()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: wxgAllergyManagerDlg.__do_layout
        __szr_main = wx.BoxSizer(wx.VERTICAL)
        __szr_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.__szr_details_staticbox.Lower()
        __szr_details = wx.StaticBoxSizer(self.__szr_details_staticbox, wx.VERTICAL)
        __szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.__szr_state_staticbox.Lower()
        __szr_state = wx.StaticBoxSizer(self.__szr_state_staticbox, wx.VERTICAL)
        __szr_state_button = wx.BoxSizer(wx.HORIZONTAL)
        __gszr_state = wx.FlexGridSizer(4, 2, 2, 10)
        __szr_new_state = wx.BoxSizer(wx.HORIZONTAL)
        __szr_current_state = wx.BoxSizer(wx.HORIZONTAL)
        __LBL_state = wx.StaticText(self, -1, _("Currently:"))
        __gszr_state.Add(__LBL_state, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_current_state.Add(self._TXT_current_state, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 15)
        __LBL_confirmed = wx.StaticText(self, -1, _("Last confirmed:"))
        __szr_current_state.Add(__LBL_confirmed, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        __szr_current_state.Add(self._TXT_last_confirmed, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        __gszr_state.Add(__szr_current_state, 1, wx.EXPAND, 0)
        __LBL_set_state = wx.StaticText(self, -1, _("Set to:"))
        __gszr_state.Add(__LBL_set_state, 0, wx.ALIGN_CENTER_VERTICAL, 15)
        __szr_new_state.Add(self._RBTN_unknown, 0, wx.RIGHT | wx.EXPAND, 10)
        __szr_new_state.Add(self._RBTN_none, 0, wx.RIGHT | wx.EXPAND, 10)
        __szr_new_state.Add(self._RBTN_some, 0, wx.EXPAND, 10)
        __gszr_state.Add(__szr_new_state, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        __LBL_comment = wx.StaticText(self, -1, _("Comment:"))
        __gszr_state.Add(__LBL_comment, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __gszr_state.Add(self._TCTRL_state_comment, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        __gszr_state.AddGrowableCol(1)
        __szr_state.Add(__gszr_state, 1, wx.BOTTOM | wx.EXPAND, 5)
        __szr_state_button.Add((20, 20), 1, wx.EXPAND, 0)
        __szr_state_button.Add(self._BTN_confirm, 0, wx.EXPAND, 0)
        __szr_state_button.Add((20, 20), 1, wx.EXPAND, 0)
        __szr_state.Add(__szr_state_button, 0, wx.EXPAND, 0)
        __szr_main.Add(__szr_state, 0, wx.ALL | wx.EXPAND, 5)
        __szr_details.Add(self._LCTRL_allergies, 2, wx.BOTTOM | wx.EXPAND, 10)
        __szr_details.Add(self._LBL_message, 0, wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 3)
        __szr_details.Add(self._PNL_edit_area, 2, wx.BOTTOM | wx.EXPAND, 5)
        __szr_buttons.Add(self._BTN_save_details, 0, wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        __szr_buttons.Add(self._BTN_clear, 0, wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        __szr_buttons.Add(self._BTN_delete, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        __szr_buttons.Add((20, 20), 2, wx.EXPAND, 0)
        __szr_details.Add(__szr_buttons, 0, wx.EXPAND, 5)
        __szr_main.Add(__szr_details, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
        __szr_main.Add(self.__hline_bottom, 0, wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 2)
        __szr_bottom.Add((20, 20), 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_bottom.Add(self._BTN_dismiss, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_bottom.Add((20, 20), 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_main.Add(__szr_bottom, 0, wx.TOP | wx.EXPAND, 5)
        self.SetSizer(__szr_main)
        self.Layout()
        self.Centre()
        # end wxGlade

    def _on_save_button_pressed(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_save_button_pressed' not implemented!"
        event.Skip()

    def _on_clear_button_pressed(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_clear_button_pressed' not implemented!"
        event.Skip()

    def _on_delete_button_pressed(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_delete_button_pressed' not implemented"
        event.Skip()

    def _on_list_item_deselected(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_list_item_deselected' not implemented"
        event.Skip()

    def _on_list_item_selected(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_list_item_selected' not implemented"
        event.Skip()

    def _on_list_item_activated(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_list_item_activated' not implemented"
        event.Skip()

    def _on_list_item_focused(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_list_item_focused' not implemented"
        event.Skip()

    def _on_dismiss_button_pressed(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_dismiss_button_pressed' not implemented"
        event.Skip()

    def _on_reconfirm_button_pressed(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_reconfirm_button_pressed' not implemented"
        event.Skip()

    def _on_save_state_button_pressed(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_save_state_button_pressed' not implemented"
        event.Skip()

    def _on_save_details_button_pressed(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_save_details_button_pressed' not implemented"
        event.Skip()

    def _on_confirm_button_pressed(self, event): # wxGlade: wxgAllergyManagerDlg.<event_handler>
        print "Event handler `_on_confirm_button_pressed' not implemented"
        event.Skip()

# end of class wxgAllergyManagerDlg


