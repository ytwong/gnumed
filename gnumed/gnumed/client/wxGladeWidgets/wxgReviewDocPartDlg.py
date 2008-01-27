#!/usr/bin/env python
# -*- coding: ISO-8859-15 -*-
# generated by wxGlade 0.4cvs on Wed Jul  5 00:30:46 2006

import wx

class wxgReviewDocPartDlg(wx.Dialog):
    def __init__(self, *args, **kwds):

        from Gnumed.wxpython import gmEMRStructWidgets, gmDateTimeInput, gmMedDocWidgets

        # begin wxGlade: wxgReviewDocPartDlg.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME|wx.STAY_ON_TOP
        wx.Dialog.__init__(self, *args, **kwds)
        self.__szr_box_review_staticbox = wx.StaticBox(self, -1, _("Your review"))
        self.__szr_reviews_staticbox = wx.StaticBox(self, -1, _("Reviews by others"))
        self._PhWheel_episode = gmEMRStructWidgets.cEpisodeSelectionPhraseWheel(self, -1, style=wx.NO_BORDER)
        self._PhWheel_doc_type = gmMedDocWidgets.cDocumentTypeSelectionPhraseWheel(self, -1, style=wx.NO_BORDER)
        self._PRW_doc_comment = gmMedDocWidgets.cDocumentCommentPhraseWheel(self, -1, "", style=wx.NO_BORDER)
        self._PhWheel_doc_date = gmDateTimeInput.cFuzzyTimestampInput(self, -1, style=wx.NO_BORDER)
        self._TCTRL_reference = wx.TextCtrl(self, -1, "", style=wx.NO_BORDER)
        self._TCTRL_filename = wx.TextCtrl(self, -1, "", style=wx.NO_BORDER)
        self._SPINCTRL_seq_idx = wx.SpinCtrl(self, -1, "", min=0, max=10000, style=wx.SP_ARROW_KEYS|wx.SP_WRAP|wx.TE_AUTO_URL|wx.TE_NOHIDESEL|wx.NO_BORDER)
        self._LCTRL_existing_reviews = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_ALIGN_LEFT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES|wx.NO_BORDER)
        self._TCTRL_responsible = wx.TextCtrl(self, -1, _("(you are/are not the primary reviewer)"), style=wx.TE_READONLY|wx.NO_BORDER)
        self._ChBOX_review = wx.CheckBox(self, -1, _("review document"))
        self._ChBOX_abnormal = wx.CheckBox(self, -1, _("technically abnormal"))
        self._ChBOX_responsible = wx.CheckBox(self, -1, _("take over responsibility"))
        self._ChBOX_relevant = wx.CheckBox(self, -1, _("clinically relevant"))
        self._ChBOX_sign_all_pages = wx.CheckBox(self, -1, _("sign all parts"))
        self._BTN_save = wx.Button(self, wx.ID_OK, _("Save"))
        self._BTN_cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self._on_reviewed_box_checked, self._ChBOX_review)
        self.Bind(wx.EVT_BUTTON, self._on_save_button_pressed, id=wx.ID_OK)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: wxgReviewDocPartDlg.__set_properties
        self.SetTitle(_("Edit document properties"))
        self._PhWheel_episode.SetToolTipString(_("Shows the episode associated with this document. Select another one or type in a new episode name to associate a different one."))
        self._LCTRL_existing_reviews.SetToolTipString(_("Lists previous reviews for this document part.\n\nThe first line (marked with an icon) will show your previous review if there is one.\nThe second line (marked with a blue bar) will display the review of the responsible provider if there is such a review.\n\n You can edit your review below."))
        self._LCTRL_existing_reviews.Enable(False)
        self._TCTRL_responsible.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BACKGROUND))
        self._ChBOX_review.SetToolTipString(_("Check this if you want to edit your review."))
        self._ChBOX_abnormal.Enable(False)
        self._ChBOX_responsible.SetToolTipString(_("Check this if you intend to take over responsibility for this document and not just review it."))
        self._ChBOX_responsible.Enable(False)
        self._ChBOX_relevant.Enable(False)
        self._ChBOX_sign_all_pages.SetToolTipString(_("Apply review to entire document rather than just this part or page."))
        self._ChBOX_sign_all_pages.Enable(False)
        self._ChBOX_sign_all_pages.SetValue(1)
        self._BTN_save.SetToolTipString(_("Save your review."))
        self._BTN_cancel.SetToolTipString(_("Cancel this review."))
        self._BTN_cancel.SetFocus()
        self._BTN_cancel.SetDefault()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: wxgReviewDocPartDlg.__do_layout
        __szr_main = wx.BoxSizer(wx.VERTICAL)
        __szr_bottom = wx.BoxSizer(wx.HORIZONTAL)
        __szr_box_review = wx.StaticBoxSizer(self.__szr_box_review_staticbox, wx.VERTICAL)
        __szr_grid_review = wx.FlexGridSizer(4, 2, 0, 0)
        __szr_reviews = wx.StaticBoxSizer(self.__szr_reviews_staticbox, wx.HORIZONTAL)
        __szr_grid_properties = wx.FlexGridSizer(7, 2, 2, 3)
        __lbl_episode_picker = wx.StaticText(self, -1, _("Episode"))
        __szr_grid_properties.Add(__lbl_episode_picker, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_grid_properties.Add(self._PhWheel_episode, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __lbl_type = wx.StaticText(self, -1, _("Type"))
        __szr_grid_properties.Add(__lbl_type, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_grid_properties.Add(self._PhWheel_doc_type, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __lbl_comment = wx.StaticText(self, -1, _("Comment"))
        __szr_grid_properties.Add(__lbl_comment, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_grid_properties.Add(self._PRW_doc_comment, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __lbl_doc_date = wx.StaticText(self, -1, _("Date"))
        __szr_grid_properties.Add(__lbl_doc_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_grid_properties.Add(self._PhWheel_doc_date, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __lbl_reference = wx.StaticText(self, -1, _("Reference"))
        __szr_grid_properties.Add(__lbl_reference, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_grid_properties.Add(self._TCTRL_reference, 0, wx.EXPAND, 0)
        __lbl_filename = wx.StaticText(self, -1, _("Filename"))
        __lbl_filename.SetToolTipString(_("The original filename (if any). Only editable if invoked from a single part of the document."))
        __szr_grid_properties.Add(__lbl_filename, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_grid_properties.Add(self._TCTRL_filename, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __lbl_seq_idx = wx.StaticText(self, -1, _("Seq #"))
        __lbl_seq_idx.SetToolTipString(_("The sequence index or page number. If invoked from a document instead of a page always applies to the first page."))
        __szr_grid_properties.Add(__lbl_seq_idx, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_grid_properties.Add(self._SPINCTRL_seq_idx, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        __szr_grid_properties.AddGrowableCol(1)
        __szr_main.Add(__szr_grid_properties, 0, wx.ALL|wx.EXPAND, 5)
        __szr_reviews.Add(self._LCTRL_existing_reviews, 1, wx.EXPAND, 0)
        __szr_main.Add(__szr_reviews, 1, wx.EXPAND, 0)
        __szr_box_review.Add(self._TCTRL_responsible, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        __szr_grid_review.Add(self._ChBOX_review, 0, wx.ADJUST_MINSIZE, 0)
        __szr_grid_review.Add((5, 5), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        __szr_grid_review.Add(self._ChBOX_abnormal, 0, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        __szr_grid_review.Add(self._ChBOX_responsible, 0, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        __szr_grid_review.Add(self._ChBOX_relevant, 0, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        __szr_grid_review.Add(self._ChBOX_sign_all_pages, 0, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        __szr_box_review.Add(__szr_grid_review, 1, wx.EXPAND, 0)
        __szr_main.Add(__szr_box_review, 1, wx.EXPAND, 0)
        __szr_bottom.Add(self._BTN_save, 0, wx.ADJUST_MINSIZE, 0)
        __szr_bottom.Add(self._BTN_cancel, 0, 0, 0)
        __szr_main.Add(__szr_bottom, 0, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(__szr_main)
        __szr_main.Fit(self)
        __szr_main.SetSizeHints(self)
        self.Layout()
        self.Centre()
        # end wxGlade

    def _on_reviewed_box_checked(self, event): # wxGlade: wxgReviewDocPartDlg.<event_handler>
        print "Event handler `_on_reviewed_box_checked' not implemented!"
        event.Skip()

    def _on_save_button_pressed(self, event): # wxGlade: wxgReviewDocPartDlg.<event_handler>
        print "Event handler `_on_save_button_pressed' not implemented!"
        event.Skip()

# end of class wxgReviewDocPartDlg


