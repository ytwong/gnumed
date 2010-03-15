# GnuMed

#===========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmTopPanel.py,v $
# $Id: gmTopPanel.py,v 1.106 2009-07-17 09:26:53 ncq Exp $
__version__ = "$Revision: 1.106 $"
__author__  = "R.Terry <rterry@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys, os.path, datetime as pyDT, logging


import wx


from Gnumed.pycommon import gmGuiBroker, gmPG2, gmDispatcher, gmTools, gmCfg2, gmDateTime, gmI18N
from Gnumed.business import gmPerson, gmEMRStructItems, gmAllergy
from Gnumed.wxpython import gmGuiHelpers, gmPatPicWidgets, gmPatSearchWidgets, gmAllergyWidgets

_log = logging.getLogger('gm.ui')
_log.info(__version__)

[	ID_BTN_pat_demographics,
#	ID_CBOX_consult_type,
	ID_BMITOOL,
	ID_BMIMENU,
	ID_PREGTOOL,
	ID_PREGMENU,
	ID_LOCKBUTTON,
	ID_LOCKMENU,
] = map(lambda _init_ctrls: wx.NewId(), range(7))

# FIXME: need a better name here !
bg_col = wx.Colour(214,214,214)
fg_col = wx.Colour(0,0,131)
col_brightred = wx.Colour(255,0,0)
#===========================================================
class cMainTopPanel(wx.Panel):

	def __init__(self, parent, id):

		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER)

		self.__gb = gmGuiBroker.GuiBroker()

		self.__do_layout()
		self.__register_interests()

		# init plugin toolbars dict
		#self.subbars = {}
		self.curr_pat = gmPerson.gmCurrentPatient()

		# and actually display ourselves
		self.SetAutoLayout(True)
		self.Show(True)
	#-------------------------------------------------------
	def __do_layout(self):
		"""Create the layout.

		.--------------------------------.
		| patient | top row              |
		| picture |----------------------|
		|         | bottom row           |
		`--------------------------------'
		"""
		self.SetBackgroundColour(bg_col)

		# create rows
		# - top row
		# .--------------------------------------.
		# | details | patient  | age | allergies |
		# | button  | selector |     |           |
		# `--------------------------------------'
		self.szr_top_row = wx.BoxSizer(wx.HORIZONTAL)

		#  - details button
#		fname = os.path.join(self.__gb['gnumed_dir'], 'bitmaps', 'binoculars_form.png')
#		img = wxImage(fname, wx.BITMAP_TYPE_ANY)
#		bmp = wx.BitmapFromImage(img)
#		self.btn_pat_demographics = wx.BitmapButton (
#			parent = self,
#			id = ID_BTN_pat_demographics,
#			bitmap = bmp,
#			style = wx.BU_EXACTFIT | wxNO_BORDER
#		)
#		self.btn_pat_demographics.SetToolTip(wxToolTip(_("display patient demographics")))
#		self.szr_top_row.Add (self.btn_pat_demographics, 0, wxEXPAND | wx.BOTTOM, 3)

		# padlock button - Dare I say HIPAA ?
#		fname = os.path.join(self.__gb['gnumed_dir'], 'bitmaps', 'padlock_closed.png')
#		img = wxImage(fname, wx.BITMAP_TYPE_ANY)
#		bmp = wx.BitmapFromImage(img)
#		self.btn_lock = wx.BitmapButton (
#			parent = self,
#			id = ID_LOCKBUTTON,
#			bitmap = bmp,
#			style = wx.BU_EXACTFIT | wxNO_BORDER
#		)
#		self.btn_lock.SetToolTip(wxToolTip(_('lock client')))
#		self.szr_top_row.Add(self.btn_lock, 0, wxALL, 3)

		#  - patient selector
		self.patient_selector = gmPatSearchWidgets.cActivePatientSelector(self, -1)
		cfg = gmCfg2.gmCfgData()
		if cfg.get(option = 'slave'):
			self.patient_selector.SetEditable(0)
			self.patient_selector.SetToolTip(None)
		self.patient_selector.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))

		#  - age
		self.lbl_age = wx.StaticText(self, -1, u'', style = wx.ALIGN_CENTER_VERTICAL)
		self.lbl_age.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))

		#  - allergies (substances only, like "makrolides, penicillins, eggs")
		self.lbl_allergies = wx.StaticText (self, -1, _('Caveat'), style = wx.ALIGN_CENTER_VERTICAL)
		self.lbl_allergies.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))
		self.lbl_allergies.SetBackgroundColour(bg_col)
		self.lbl_allergies.SetForegroundColour(col_brightred)
		self.txt_allergies = wx.TextCtrl (self, -1, "", style = wx.TE_READONLY)
		self.txt_allergies.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))
		self.txt_allergies.SetForegroundColour (col_brightred)

		self.szr_top_row.Add(self.patient_selector, 6, wx.LEFT | wx.BOTTOM, 3)
		self.szr_top_row.Add(self.lbl_age, 0, wx.ALL, 3)
		self.szr_top_row.Add(self.lbl_allergies, 0, wx.ALL, 3)
		self.szr_top_row.Add(self.txt_allergies, 8, wx.BOTTOM, 3)

		# - bottom row
		# .----------------------------------------------------------.
		# | plugin toolbar | bmi | edc |          | encounter | lock |
		# |                |     |     |          | type sel  |      |
		# `----------------------------------------------------------'
		#self.tb_lock.AddControl(wx.StaticBitmap(self.tb_lock, -1, getvertical_separator_thinBitmap(), wx.DefaultPosition, wx.DefaultSize))

		# (holds most of the buttons)
		self.szr_bottom_row = wx.BoxSizer(wx.HORIZONTAL)
		self.pnl_bottom_row = wx.Panel(self, -1)
		self.szr_bottom_row.Add(self.pnl_bottom_row, 6, wx.GROW, 0)

		# BMI calculator button
#		fname = os.path.join(self.__gb['gnumed_dir'], 'bitmaps', 'bmi_calculator.png')
#		img = wx.Image(fname, wx.BITMAP_TYPE_ANY)
#		bmp = wx.BitmapFromImage(img)
#		self.btn_bmi = wx.BitmapButton (
#			parent = self,
#			id = ID_BMITOOL,
#			bitmap = bmp,
#			style = wx.BU_EXACTFIT | wx.NO_BORDER
#		)
#		self.btn_bmi.SetToolTip(wx.ToolTip(_("BMI Calculator")))
#		self.szr_bottom_row.Add(self.btn_bmi, 0)

#		tb = wxToolBar(self, -1, style=wx.TB_HORIZONTAL | wxNO_BORDER | wx.TB_FLAT)
#		tb.AddTool (
#			ID_BMITOOL,
#			gmImgTools.xpm2bmp(bmicalculator.get_xpm()),
#			shortHelpString = _("BMI Calculator")
#		)
#		self.szr_bottom_row.Add(tb, 0, wxRIGHT, 0)

		# pregnancy calculator button
#		fname = os.path.join(self.__gb['gnumed_dir'], 'bitmaps', 'preg_calculator.png')
#		img = wxImage(fname, wx.BITMAP_TYPE_ANY)
#		bmp = wx.BitmapFromImage(img)
#		self.btn_preg = wx.BitmapButton (
#			parent = self,
#			id = ID_PREGTOOL,
#			bitmap = bmp,
#			style = wx.BU_EXACTFIT | wxNO_BORDER
#		)
#		self.btn_preg.SetToolTip(wxToolTip(_("Pregnancy Calculator")))
#		self.szr_bottom_row.Add(self.btn_preg, 0)

		# - stack them atop each other
		self.szr_stacked_rows = wx.BoxSizer(wx.VERTICAL)
		# ??? (IMHO: space is at too much of a premium for such padding)
		# FIXME: deuglify
		try:
			self.szr_stacked_rows.Add(1, 1, 0)
		except:
			self.szr_stacked_rows.Add((1, 1), 0)

		# 0 here indicates the sizer cannot change its heights - which is intended
		self.szr_stacked_rows.Add(self.szr_top_row, 0, wx.EXPAND)
		self.szr_stacked_rows.Add(self.szr_bottom_row, 1, wx.EXPAND|wx.TOP, 5)

		# create patient picture
		self.patient_picture = gmPatPicWidgets.cPatientPicture(self, -1)
		tt = wx.ToolTip(_('Patient picture.\nRight-click for context menu.'))
		self.patient_picture.SetToolTip(tt)

		# create main sizer
		self.szr_main = wx.BoxSizer(wx.HORIZONTAL)
		# - insert patient picture
		self.szr_main.Add(self.patient_picture, 0, wx.LEFT | wx.TOP | wx.Right, 5)
		# - insert stacked rows
		self.szr_main.Add(self.szr_stacked_rows, 1)

		# associate ourselves with our main sizer
		self.SetSizer(self.szr_main)
		# and auto-size to minimum calculated size
		self.szr_main.Fit(self)
	#-------------------------------------------------------
	# internal helpers
	#-------------------------------------------------------
	#-------------------------------------------------------
	# event handling
	#-------------------------------------------------------
	def __register_interests(self):
		# events
		wx.EVT_BUTTON(self, ID_BTN_pat_demographics, self.__on_display_demographics)

#		tools_menu = self.__gb['main.toolsmenu']

		# - BMI calculator
#		wx.EVT_BUTTON(self, ID_BMITOOL, self._on_show_BMI)
#		tools_menu.Append(ID_BMIMENU, _("BMI"), _("Body Mass Index Calculator"))
#		wx.EVT_MENU(main_frame, ID_BMIMENU, self._on_show_BMI)

		# - pregnancy calculator
#		wx.EVT_BUTTON(self, ID_PREGTOOL, self._on_show_Preg_Calc)
#		tools_menu.Append(ID_PREGMENU, _("EDC"), _("Pregnancy Calculator"))
#		wx.EVT_MENU(main_frame, ID_PREGMENU, self._on_show_Preg_Calc)

		# - lock button
#		wx.EVT_BUTTON(self, ID_LOCKBUTTON, self._on_lock)
#		tools_menu.Append(ID_LOCKMENU, _("lock client"), _("locks client and hides data"))
#		wx.EVT_MENU(main_frame, ID_LOCKMENU, self._on_lock)

		wx.EVT_LEFT_DCLICK(self.txt_allergies, self._on_allergies_dclicked)

		# client internal signals
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'allg_mod_db', receiver = self._update_allergies)
		gmDispatcher.connect(signal = u'allg_state_mod_db', receiver = self._update_allergies)
		gmDispatcher.connect(signal = u'name_mod_db', receiver = self._on_name_identity_change)
		gmDispatcher.connect(signal = u'identity_mod_db', receiver = self._on_name_identity_change)
	#----------------------------------------------
#	def _on_lock(self, evt):
#		print "should be locking client now by obscuring data"
#		print "and popping up a modal dialog box asking for a"
#		print "password to reactivate"
	#----------------------------------------------
	def _on_allergies_dclicked(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send('statustext', msg = _('Cannot activate Allergy Manager. No active patient.'))
			return
		dlg = gmAllergyWidgets.cAllergyManagerDlg(parent=self, id=-1)
		dlg.ShowModal()
		return
	#----------------------------------------------
#	def _on_show_BMI(self, evt):
		# FIXME: update patient ID ?
#		bmi = gmBMIWidgets.BMI_Frame(self)
#		bmi.Centre(wx.BOTH)
#		bmi.Show(1)
	#----------------------------------------------
#	def _on_show_Preg_Calc(self, evt):
		# FIXME: update patient ID ?
#		pc = gmPregWidgets.cPregCalcFrame(self)
#		pc.Centre(wx.BOTH)
#		pc.Show(1)
	#----------------------------------------------
	def _on_name_identity_change(self):
		wx.CallAfter(self.__on_name_identity_change)
	#----------------------------------------------
	def __on_name_identity_change(self):
		self.__update_age_label()
		self.Layout()
	#----------------------------------------------
	def _on_post_patient_selection(self, **kwargs):
		# needed because GUI stuff can't be called from a thread (and that's
		# where we are coming from via backend listener -> dispatcher)
		wx.CallAfter(self.__on_post_patient_selection, **kwargs)
	#----------------------------------------------
	def __on_post_patient_selection(self, **kwargs):
		self.__update_age_label()
		self.__update_allergies()
		self.Layout()
	#-------------------------------------------------------
	def __on_display_demographics(self, evt):
		print "display patient demographic window now"
	#-------------------------------------------------------
	def _update_allergies(self, **kwargs):
		wx.CallAfter(self.__update_allergies)
	#-------------------------------------------------------
	# internal API
	#-------------------------------------------------------
	def __update_age_label(self):

		if self.curr_pat['deceased'] is None:

			if self.curr_pat.get_formatted_dob(format = '%m-%d') == pyDT.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone).strftime('%m-%d'):
				template = _('%s  %s (%s today !)')
			else:
				template = u'%s  %s (%s)'

			# FIXME: if the age is below, say, 2 hours we should fire
			# a timer here that updates the age in increments of 1 minute ... :-)
			age = template % (
				gmPerson.map_gender2symbol[self.curr_pat['gender']],
				self.curr_pat.get_formatted_dob(format = '%d %b %Y', encoding = gmI18N.get_encoding()),
				self.curr_pat['medical_age']
			)

			# Easter Egg ;-)
			if self.curr_pat['lastnames'] == u'Leibner':
				if self.curr_pat['firstnames'] == u'Steffi':
					if self.curr_pat['preferred'] == u'Wildfang':
						age = u'%s %s' % (gmTools.u_black_heart, age)

		else:

			template = u'%s  %s - %s (%s)'
			age = template % (
				gmPerson.map_gender2symbol[self.curr_pat['gender']],
				self.curr_pat.get_formatted_dob(format = '%d.%b %Y', encoding = gmI18N.get_encoding()),
				self.curr_pat['deceased'].strftime('%d.%b %Y').decode(gmI18N.get_encoding()),
				self.curr_pat['medical_age']
			)

		self.lbl_age.SetLabel(age)
	#-------------------------------------------------------
	def __update_allergies(self, **kwargs):

		emr = self.curr_pat.get_emr()
		state = emr.allergy_state

		# state in tooltip
		if state['last_confirmed'] is None:
			confirmed = _('never')
		else:
			confirmed = state['last_confirmed'].strftime('%Y %B %d').decode(gmI18N.get_encoding())
		tt = (state.state_string + (90 * u' '))[:90] + u'\n'
		tt += _('last confirmed %s\n') % confirmed
		tt += gmTools.coalesce(state['comment'], u'', _('Comment (%s): %%s') % state['modified_by'])
		tt += u'\n'

		# allergies
		tmp = []
		for allergy in emr.get_allergies():
			# in field: "true" allergies only, not intolerances
			if allergy['type'] == 'allergy':
				tmp.append(allergy['descriptor'][:10] + gmTools.u_ellipsis)
			# in tooltip
			if allergy['definite']:
				certainty = _('definite')
			else:
				certainty = _('suspected')
			reaction = gmTools.coalesce(allergy['reaction'], _('reaction not recorded'))
			if len(reaction) > 50:
				reaction = reaction[:50] + gmTools.u_ellipsis
			tt += u'%s (%s, %s): %s\n' % (
				allergy['descriptor'],
				allergy['l10n_type'],
				certainty,
				reaction
			)

		if len(tmp) == 0:
			tmp = state.state_symbol
		else:
			tmp = ','.join(tmp)

		if state['last_confirmed'] is not None:
			tmp += state['last_confirmed'].strftime(' (%x)')

		self.txt_allergies.SetValue(tmp)
		self.txt_allergies.SetToolTipString(tt)
	#-------------------------------------------------------
	# remote layout handling
	#-------------------------------------------------------
	def AddWidgetRightBottom (self, widget):
		"""Insert a widget on the right-hand side of the bottom toolbar.
		"""
		self.szr_bottom_row.Add(widget, 0, wx.RIGHT, 0)
	#-------------------------------------------------------
	def AddWidgetLeftBottom (self, widget):
		"""Insert a widget on the left-hand side of the bottom toolbar.
		"""
		self.szr_bottom_row.Prepend(widget, 0, wx.ALL, 0)
	#-------------------------------------------------------
#	def CreateBar(self):
#		"""Creates empty toolbar suited for adding to top panel."""
#		bar = wx.ToolBar (
#			self.pnl_bottom_row,
#			-1,
#			size = self.pnl_bottom_row.GetClientSize(),
#			style = wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT
#		)
#		return bar
	#-------------------------------------------------------
#	def AddBar(self, key=None, bar=None):
#		"""Creates and returns a new empty toolbar, referenced by key.
#
#		Key should correspond to the notebook page number as defined
#		by the notebook (see gmPlugin.py), so that gmGuiMain can
#		display the toolbar with the notebook
#		"""
#		bar.SetToolBitmapSize((16,16))
#		self.subbars[key] = bar
#		if len(self.subbars) == 1:
#			bar.Show(1)
#			self.__current = key
#		else:
#			bar.Hide()
#		return True
	#-------------------------------------------------------
#	def ReFit (self):
#		"""Refits the toolbar after its been changed
#		"""
#		tw = 0
#		th = 0
#		# get maximum size for the toolbar
#		for i in self.subbars.values ():
#			ntw, nth = i.GetSizeTuple ()
#			if ntw > tw:
#				tw = ntw
#			if nth > th:
#				th = nth
#		#import pdb
#		#pdb.set_trace ()
#		sz = wx.Size (tw, th)
#		self.pnl_bottom_row.SetSize(sz)
#		for i in self.subbars.values():
#			i.SetSize (sz)
#		self.szr_main.Layout()
#		self.szr_main.Fit(self)
	#-------------------------------------------------------
#	def ShowBar (self, key):
#		"""Displays the named toolbar.
#		"""
#		self.subbars[self.__current].Hide()
#		try:
#			self.subbars[key].Show(1)
#			self.__current = key
#		except KeyError:
#			_log.exception("cannot show undefined toolbar [%s]" % key)
	#-------------------------------------------------------
#	def DeleteBar (self, key):
#		"""Removes a toolbar.
#		"""
#		try:
#			self.subbars[key].Destroy()
#			del self.subbars[key]
#			# FIXME: ??
#			if self.__current == key and len(self.subbars):
#				self.__current = self.subbars.keys()[0]
#				self.subbars[self.__current].Show(1)
#		except KeyError:
#			_log.exception("cannot delete undefined toolbar [%s]" % key)

#===========================================================	
if __name__ == "__main__":
	wx.InitAllImageHandlers()
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(cMainTopPanel, -1)
	app.MainLoop()
#===========================================================
# $Log: gmTopPanel.py,v $
# Revision 1.106  2009-07-17 09:26:53  ncq
# - no more main.frame in gui broker
#
# Revision 1.105  2009/07/15 12:47:57  ncq
# - properly display age of dead people
#
# Revision 1.104  2009/06/20 22:39:50  ncq
# - remove lock menu item
#
# Revision 1.103  2009/06/04 16:33:51  ncq
# - adjust to dob-less persons
#
# Revision 1.102  2009/03/10 14:24:53  ncq
# - refactor age label calculation
#
# Revision 1.101  2008/12/09 23:43:50  ncq
# - cleanup
#
# Revision 1.100  2008/10/22 12:22:26  ncq
# - improved allergies tooltip and display
#
# Revision 1.99  2008/10/12 16:36:45  ncq
# - cleanup
# - consultation -> encounter
# - improved allergies handling
#
# Revision 1.98  2008/08/28 18:34:47  ncq
# - pat search widget now takes care of updating
#   its display itself when necessary
#
# Revision 1.97  2008/08/05 16:22:44  ncq
# - improve dob display and allergies tooltip
#
# Revision 1.96  2008/07/10 08:41:09  ncq
# - comment out toolbar handling
# - pat.is_connected -> connected property
#
# Revision 1.95  2008/03/09 20:18:56  ncq
# - use cActivePatientSelector()
#
# Revision 1.94  2008/03/05 22:30:15  ncq
# - new style logging
#
# Revision 1.93  2008/01/27 21:20:58  ncq
# - no more label "Patient"
# - make age field a dynamically adjusting static text, include gender and DOB
# - remind of birthday
#
# Revision 1.92  2007/12/23 22:04:19  ncq
# - no more gmCLI
#
# Revision 1.91  2007/12/23 20:29:57  ncq
# - use gmCfg2
#
# Revision 1.90  2007/12/11 12:49:26  ncq
# - explicit signal handling
#
# Revision 1.89  2007/12/02 11:00:58  ncq
# - update age, too, on pat identity change
#
# Revision 1.88  2007/11/28 22:36:41  ncq
# - listen on identity/name changes for current patient
#
# Revision 1.87  2007/10/25 12:27:29  ncq
# - cleanup
#
# Revision 1.86  2007/10/25 12:21:39  ncq
# - listen to the proper signals for allergy changes
#
# Revision 1.85  2007/08/12 00:12:41  ncq
# - no more gmSignals.py
#
# Revision 1.84  2007/05/21 17:13:43  ncq
# - translate "Allergies" in allergy field tooltip
#
# Revision 1.83  2007/04/11 20:47:13  ncq
# - no more 'resource dir' and 'gnumed_dir'
#
# Revision 1.82  2007/03/26 16:50:14  ncq
# - allergy['reaction'] can be empty
#
# Revision 1.81  2007/03/26 14:44:36  ncq
# - left align first line of allergies list tooltip
#
# Revision 1.80  2007/03/23 15:39:02  ncq
# - show allergy manager on double-clicking allergies field
#
# Revision 1.79  2007/03/23 15:03:02  ncq
# - improved allergies display
#   - smaller font
#   - 10 char truncation
#   - align properly
#   - patient dependant tooltip listing allergy details including sensitivities
#
# Revision 1.78  2007/03/21 08:14:32  ncq
# - use proper no-allergies string
#
# Revision 1.77  2007/02/22 17:41:13  ncq
# - adjust to gmPerson changes
#
# Revision 1.76  2006/11/05 16:04:45  ncq
# - some cleanup
#
# Revision 1.75  2006/10/25 07:21:57  ncq
# - no more gmPG
#
# Revision 1.74  2006/07/30 21:15:53  ncq
# - do not import preg widgets
#
# Revision 1.73  2006/07/22 12:51:13  ncq
# - deactivate bmi until it is cleaned up
#
# Revision 1.72  2006/07/19 20:29:50  ncq
# - import cleanup
#
# Revision 1.71  2006/06/28 10:18:40  ncq
# - comment out consultation type selector for now
#
# Revision 1.70  2006/05/15 13:36:00  ncq
# - signal cleanup:
#   - activating_patient -> pre_patient_selection
#   - patient_selected -> post_patient_selection
#
# Revision 1.69  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.68  2005/11/27 12:56:45  ncq
# - use gmEMRStructItems.get_encounter_types()
#
# Revision 1.67  2005/09/28 21:38:11  ncq
# - more 2.6-ification
#
# Revision 1.66  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.65  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.64  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.63  2005/09/24 09:17:29  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.62  2005/09/04 07:34:31  ncq
# - comment out padlock button for now
# - add label "Patient" in front of patient search field as per Hilmar's request
#
# Revision 1.61  2005/07/24 11:40:21  ncq
# - comment out edc/pregnancy calculator
#
# Revision 1.60  2005/06/24 22:17:08  shilbert
# - deuglyfied , reclaim wasted gui sapce in TopPanel
#
# Revision 1.59  2005/05/17 08:12:11  ncq
# - move padlock tool button to inbetween patient picture and patient name
#   as users found that more consistent and drop "demographic details" tool
#   button from there
#
# Revision 1.58  2005/04/03 20:13:35  ncq
# - episode selector in top panel didn't help very much as we
#   always work on several episodes - just as the patient suffers
#   several problems at once
#
# Revision 1.57  2005/02/03 20:19:16  ncq
# - get_demographic_record() -> get_identity()
#
# Revision 1.56  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.55  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.54  2004/10/17 16:01:44  ncq
# - the FIXME said DEuglify, not MORE
#
# Revision 1.53  2004/10/16 22:42:12  sjtan
#
# script for unitesting; guard for unit tests where unit uses gmPhraseWheel; fixup where version of wxPython doesn't allow
# a child widget to be multiply inserted (gmDemographics) ; try block for later versions of wxWidgets that might fail
# the Add (.. w,h, ... ) because expecting Add(.. (w,h) ...)
#
# Revision 1.52  2004/10/14 12:13:58  ncq
# - factor out toolbar creation from toolbar registering
#
# Revision 1.51  2004/09/13 09:26:16  ncq
# - --slave -> 'main.slave_mode'
#
# Revision 1.50  2004/08/20 06:48:31  ncq
# - import gmPatSearchWidgets
#
# Revision 1.49  2004/08/18 10:16:03  ncq
# - import patient picture code from Richard's improved gmPatPicWidgets
#
# Revision 1.48  2004/08/09 00:05:15  ncq
# - cleanup
# - hardcode loading depluginized preg calculator/lock button
# - load icons from png files
#
# Revision 1.47  2004/08/06 09:25:36  ncq
# - always load BMI calculator
#
# Revision 1.46  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.45  2004/07/15 20:39:51  ncq
# - normalize/cleanup layout, I'm sure Richard will have a
#   say on this but it does look cleaner to me
#
# Revision 1.44  2004/06/26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.43  2004/06/13 22:18:41  ncq
# - cleanup
#
# Revision 1.42  2004/06/02 00:00:47  ncq
# - make work on Mac AND 2.4.1 Linux wxWidgets
# - correctly handle episode VOs
#
# Revision 1.41  2004/05/30 09:03:46  shilbert
# - one more little fix regarding get_active_episode()
#
# Revision 1.40  2004/05/29 22:19:56  ncq
# - use get_active_episode()
#
# Revision 1.39  2004/05/28 09:03:54  shilbert
# - fix sizer setup to enable it on wxMac
#
# Revision 1.38  2004/05/18 22:39:15  ncq
# - work with episode objects now
#
# Revision 1.37  2004/05/18 20:43:17  ncq
# - check get_clinical_record() return status
#
# Revision 1.36  2004/05/16 14:32:51  ncq
# - cleanup
#
# Revision 1.35  2004/05/08 17:34:15  ncq
# - v_i18n_enum_encounter_type is gone, use _(encounter_type)
#
# Revision 1.34  2004/04/20 00:17:55  ncq
# - allergies API revamped, kudos to Carlos
#
# Revision 1.33  2004/03/25 11:03:23  ncq
# - getActiveName -> get_names
#
# Revision 1.32  2004/03/04 19:47:07  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.31  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.30  2004/02/18 14:03:37  ncq
# - hardcode encounter type "chart review", too
#
# Revision 1.29  2004/02/12 23:58:17  ncq
# - disable editing of patient selector when --slave()d
#
# Revision 1.28  2004/02/05 23:49:52  ncq
# - use wxCallAfter()
#
# Revision 1.27  2004/01/15 14:58:31  ncq
# - activate episode selector
#
# Revision 1.26  2004/01/06 10:07:42  ncq
# - add episode selector to the left of the encounter type selector
#
# Revision 1.25  2003/11/18 23:48:08  ncq
# - remove merge conflict remnants in update_allergy
#
# Revision 1.24  2003/11/17 10:56:39  sjtan
#
# synced and commiting.
#
# Revision 1.23  2003/11/13 08:15:25  ncq
# - display allergies in top panel again
#
# Revision 1.22  2003/11/09 17:33:27  shilbert
# - minor glitch
#
# Revision 1.21  2003/11/09 17:31:13  shilbert
# - ['demographics'] -> ['demographic record']
#
# Revision 1.20  2003/11/09 14:31:25  ncq
# - new API style in clinical record
# Revision 1.19  2003/10/26 18:04:01  ncq
# - cleanup
#
# Revision 1.18  2003/10/26 11:27:10  ihaywood
# gmPatient is now the "patient stub", all demographics stuff in gmDemographics.
#
# Ergregious breakages are fixed, but needs more work
#
# Revision 1.17  2003/10/26 01:36:14  ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.16  2003/10/19 12:20:10  ncq
# - use GuiHelpers.py
#
# Revision 1.15  2003/07/07 08:34:31  ihaywood
# bugfixes on gmdrugs.sql for postgres 7.3
#
# Revision 1.14  2003/06/26 21:40:29  ncq
# - fatal->verbose
#
# Revision 1.13  2003/06/26 04:18:40  ihaywood
# Fixes to gmCfg for commas
#
# Revision 1.12  2003/06/01 12:31:58  ncq
# - logging data is not by any means lInfo
#
# Revision 1.11  2003/06/01 01:47:33  sjtan
#
# starting allergy connections.
#
# Revision 1.10  2003/05/05 00:21:00  ncq
# - make work with encounter types translation
#
# Revision 1.9  2003/05/05 00:00:21  ncq
# - do load encounter types again
#
# Revision 1.8  2003/05/04 23:33:56  ncq
# - comments bettered
#
# Revision 1.7  2003/05/03 14:18:06  ncq
# - must use wxCallAfter in _update_allergies since this can be called
#   indirectly from a thread listening to backend signals and one cannot use
#   wx GUI functions from Python threads other than main()
#
# Revision 1.6  2003/05/03 00:43:14  ncq
# - properly set allergies field on patient change
# - hot update of allergies in DB needs testing
#
# Revision 1.5  2003/05/01 15:04:10  ncq
# - connect allergies field to backend (need to filter out sensitivities, though)
# - update allergies on patient selection
# - listen to allergy change signal
#
# Revision 1.4  2003/04/28 12:05:21  ncq
# - use plugin.internal_name(), cleaner logging
#
# Revision 1.3  2003/04/25 13:37:22  ncq
# - moved combo box "consultation type" here from gmDemographics (still needs to be placed right-most)
# - helper __show_error()
# - connected "consultation type" to backend
#
# Revision 1.2  2003/04/19 15:00:30  ncq
# - display age, finally
#
# Revision 1.1  2003/04/08 21:24:14  ncq
# - renamed gmGP_Toolbar -> gmTopPanel
#
# Revision 1.13  2003/04/04 20:43:01  ncq
# - install new patient search widget
# - rework to be a more invariant top pane less dependant on gmDemographics
# - file should be renamed to gmTopPane.py
#
# Revision 1.12  2003/03/29 18:26:04  ncq
# - allow proportion/flag/border in AddWidgetTopLine()
#
# Revision 1.11  2003/03/29 13:46:44  ncq
# - make standalone work, cure sizerom
# - general cleanup, comment, clarify
#
# Revision 1.10  2003/01/12 00:24:02  ncq
# - CVS keywords
#
