# GnuMed
# GPL

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmTopPanel.py,v $
__version__ = "$Revision: 1.47 $"
__author__  = "R.Terry <rterry@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>, K.Hilbert <Karsten.Hilbert@gmx.net>"
#===========================================================
import sys, os.path, cPickle, zlib, string

from Gnumed.pycommon import gmGuiBroker, gmPG, gmSignals, gmDispatcher, gmLog, gmCLI
from Gnumed.business import gmPatient
from Gnumed.wxpython import gmGP_PatientPicture, gmPatientSelector, gmGuiHelpers, gmBMIWidgets
from Gnumed.pycommon.gmPyCompat import *

from wxPython.wx import *

_log = gmLog.gmDefLog

ID_BTN_pat_demographics = wxNewId()
ID_CBOX_consult_type = wxNewId()
ID_CBOX_episode = wxNewId()
ID_BMITOOL = wxNewId()
ID_BMIMENU = wxNewId()

# FIXME: need a better name here !
bg_col = wxColour(214,214,214)
fg_col = wxColour(0,0,131)
col_brightred = wxColour(255,0,0)
#===========================================================
class cMainTopPanel(wxPanel):

	__icons = {
"""icon_binoculars_form""": 'x\xdam\x8e\xb1\n\xc4 \x0c\x86\xf7>\x85p\x83\x07\x01\xb9.\xa7\xb3\x16W\x87.]\
K\xc7+x\xef?]L\xa2\xb5r!D\xbe\x9f/\xc1\xe7\xf9\x9d\xa7U\xcfo\x85\x8dCO\xfb\
\xaaA\x1d\xca\x9f\xfb\xf1!RH\x8f\x17\x96u\xc4\xa9\xb0u6\x08\x9b\xc2\x8b[\xc2\
\xc2\x9c\x0bG\x17Cd\xde\n{\xe7\x83wr\xef*\x83\xc5\xe1\xa6Z_\xe1_3\xb7\xea\
\xc3\x94\xa4\x07\x13\x00h\xdcL\xc8\x90\x12\x8e\xd1\xa4\xeaM\xa0\x94\xf7\x9bI\
\x92\xa8\xf5\x9f$\x19\xd69\xc43rp\x08\xb3\xac\xe7!4\xf5\xed\xd7M}kx+\x0c\xcd\
\x0fE\x94aS'
}

	def __init__(self, parent, id):

		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxRAISED_BORDER)

		self.__gb = gmGuiBroker.GuiBroker()

		self.__load_consultation_types()
		self.__do_layout()
		del self.__consultation_types
		self.__register_interests()

		# init plugin toolbars dict
		self.subbars = {}
		self.curr_pat = gmPatient.gmCurrentPatient()

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
		self.szr_top_row = wxBoxSizer (wxHORIZONTAL)

		#  - details button
		bmp = wxBitmapFromXPMData(cPickle.loads(zlib.decompress(self.__icons[_("icon_binoculars_form")])))
		self.btn_pat_demographics = wxBitmapButton (
			parent = self,
			id = ID_BTN_pat_demographics,
			bitmap = bmp,
			style = wxBU_EXACTFIT | wxNO_BORDER
		)
		self.btn_pat_demographics.SetToolTip(wxToolTip(_("display patient demographics")))
		self.szr_top_row.Add (self.btn_pat_demographics, 0, wxEXPAND | wxBOTTOM, 3)
		#  - patient selector
		self.patient_selector = gmPatientSelector.cPatientSelector(self, -1)
		if gmCLI.has_arg('--slave'):
			self.patient_selector.SetEditable(0)
			self.patient_selector.SetToolTip(None)
		self.patient_selector.SetFont(wxFont(12, wxSWISS, wxNORMAL, wxBOLD, False, ''))
		self.szr_top_row.Add (self.patient_selector, 5, wxEXPAND | wxBOTTOM, 3)
		#  - age
#		self.lbl_age = wxStaticText (self, -1, _("Age"), style = wxALIGN_CENTER_VERTICAL)
#		self.lbl_age.SetFont (wxFont(12, wxSWISS, wxNORMAL, wxBOLD, False, ''))
		self.txt_age = wxTextCtrl (self, -1, "", size = (50,-1), style = wxTE_READONLY)
		self.txt_age.SetFont (wxFont(12, wxSWISS, wxNORMAL, wxBOLD, False, ''))
		self.txt_age.SetBackgroundColour(bg_col)
#		self.szr_top_row.Add (self.lbl_age, 0, wxEXPAND | wxALIGN_CENTER_VERTICAL | wxALL, 3)
		self.szr_top_row.Add (self.txt_age, 0, wxEXPAND | wxBOTTOM | wxLEFT | wxRIGHT, 3)
		#  - allergies (substances only, like "makrolides, penicillins, eggs")
		self.lbl_allergies = wxStaticText (self, -1, _("Allergies"), style = wxALIGN_CENTER_VERTICAL)
		self.lbl_allergies.SetFont(wxFont(12, wxSWISS, wxNORMAL, wxBOLD, False, ''))
		self.lbl_allergies.SetBackgroundColour(bg_col)
		self.lbl_allergies.SetForegroundColour(col_brightred)
		self.txt_allergies = wxTextCtrl (self, -1, "", style = wxTE_READONLY)
		self.txt_allergies.SetFont(wxFont(12, wxSWISS, wxNORMAL, wxBOLD, False, ''))
		self.txt_allergies.SetBackgroundColour(bg_col)
		self.txt_allergies.SetForegroundColour (col_brightred)
		self.szr_top_row.Add (self.lbl_allergies, 0, wxEXPAND | wxBOTTOM, 3)
		self.szr_top_row.Add (self.txt_allergies, 6, wxEXPAND | wxBOTTOM, 3)

		# - bottom row
		# (holds most of the buttons)
		self.szr_bottom_row = wxBoxSizer (wxHORIZONTAL)
		self.pnl_bottom_row = wxPanel(self, -1)
		self.szr_bottom_row.Add(self.pnl_bottom_row, 6, wxGROW, 0)

		# BMI calculator button
		png_fname = os.path.join(self.__gb['gnumed_dir'], 'icons', 'bmi.png')
		bmp = wxBitmap(png_fname, wxBITMAP_TYPE_PNG)
		self.btn_bmi = wxBitmapButton (
			parent = self,
			id = ID_BMITOOL,
			bitmap = bmp,
			style = wxBU_EXACTFIT | wxNO_BORDER
		)
		self.btn_bmi.SetToolTip(wxToolTip(_("BMI Calculator")))
		self.szr_bottom_row.Add(self.btn_bmi, 0, wxEXPAND | wxBOTTOM, 3)

#		tb = wxToolBar(self, -1, style=wxTB_HORIZONTAL | wxNO_BORDER | wxTB_FLAT)
#		tb.AddTool (
#			ID_BMITOOL,
#			gmImgTools.xpm2bmp(bmicalculator.get_xpm()),
#			shortHelpString = _("BMI Calculator")
#		)
#		self.szr_bottom_row.Add(tb, 0, wxRIGHT, 0)

		# episode selector
		# FIXME: handle input -> new episode
		# FIXME: should be cEpisodeSelector class
		self.combo_episodes = wxComboBox (
			self,
			ID_CBOX_episode,
			'',
			wxPyDefaultPosition,
			wxPyDefaultSize,
			[],
			wxCB_DROPDOWN
		)
		tt = wxToolTip(_('choose problem to work on\nsubsequent input is attached to the corresponding episode'))
		self.combo_episodes.SetToolTip(tt)
		self.szr_bottom_row.Add(self.combo_episodes, 3, wxEXPAND, 0)
		# consultation type selector
		self.combo_consultation_type = wxComboBox (
			self,
			ID_CBOX_consult_type,
			self.DEF_CONSULT_TYPE,
			wxPyDefaultPosition,
			wxPyDefaultSize,
			self.__consultation_types,
			wxCB_DROPDOWN | wxCB_READONLY
		)
		self.combo_consultation_type.SetToolTip(wxToolTip(_('choose consultation type')))
		self.szr_bottom_row.Add(self.combo_consultation_type, 2, wxEXPAND, 0)

		# - stack them atop each other
		self.szr_stacked_rows = wxBoxSizer(wxVERTICAL)
		# FIXME: deuglify
		# ??? (IMHO: space is at too much of a premium for such padding)
		if wxPlatform == '__WXMAC__':
			self.szr_stacked_rows.Add((1, 3), 0, wxEXPAND)
		else:
			self.szr_stacked_rows.Add(1, 3, 0, wxEXPAND)
		self.szr_stacked_rows.Add(self.szr_top_row, 1, wxEXPAND)
		self.szr_stacked_rows.Add(self.szr_bottom_row, 1, wxEXPAND | wxALL, 2)

		# create patient picture
		self.patient_picture = gmGP_PatientPicture.cPatientPicture(self, -1)
		self.__gb['main.patient_picture'] = self.patient_picture

		# create main sizer
		self.szr_main = wxBoxSizer(wxHORIZONTAL)
		# - insert patient picture
		self.szr_main.Add(self.patient_picture, 0, wxEXPAND)
		# - insert stacked rows
		self.szr_main.Add(self.szr_stacked_rows, 1, wxEXPAND)

		# associate ourselves with our main sizer
		self.SetSizer(self.szr_main)
		# and auto-size to minimum calculated size
		self.szr_main.Fit(self)
	#-------------------------------------------------------
	# internal helpers
	#-------------------------------------------------------
	def __load_consultation_types(self):
		cmd = "SELECT _(description) from encounter_type"
		result = gmPG.run_ro_query('historica', cmd, None)
		if (result is None) or (len(result) == 0):
			_log.Log(gmLog.lWarn, 'cannot load consultation types from backend')
			self.__consultation_types = [_('in surgery'), _('chart review')]
			self.DEF_CONSULT_TYPE = self.__consultation_types[0]
			gmGuiHelpers.gm_show_error (
				_('Cannot load consultation types from backend.\n'
				  'Consequently, the only available type are:\n'
				  '%s') % self.__consultation_types,
				_('loading consultation types'),
				gmLog.lWarn
			)
			return None
		self.__consultation_types = []
		for cons_type in result:
			self.__consultation_types.append(cons_type[0])
		self.DEF_CONSULT_TYPE = self.__consultation_types[0]
		return 1
	#-------------------------------------------------------
	# event handling
	#-------------------------------------------------------
	def __register_interests(self):
		# events
		EVT_BUTTON(self, ID_BTN_pat_demographics, self.__on_display_demographics)

		# - BMI calculator
		EVT_BUTTON(self, ID_BMITOOL, self._on_show_BMI)
		self.__gb['main.toolsmenu'].Append(ID_BMIMENU, _("BMI"), _("Body Mass Index Calculator"))
		EVT_MENU(self.__gb['main.frame'], ID_BMIMENU, self._on_show_BMI)

		# - episode selector
		EVT_COMBOBOX(self, ID_CBOX_episode, self._on_episode_selected)

		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._on_patient_selected)
		gmDispatcher.connect(signal=gmSignals.allergy_updated(), receiver=self._update_allergies)
	#----------------------------------------------
	def _on_show_BMI(self, evt):
		# FIXME: update patient ID ?
		bmi = gmBMIWidgets.BMI_Frame(self)
		bmi.Centre(wxBOTH)
		bmi.Show(1)
	#----------------------------------------------
	def _on_episode_selected(self, evt):
		epr = self.curr_pat.get_clinical_record()
		if epr is None:
			return None
		ep_name = evt.GetString()
		if not epr.set_active_episode(ep_name):
			gmGuiHelpers.gm_show_error (
				_('Cannot activate episode [%s].\n'
				  'Leaving previous one activated.' % ep_name),
				_('selecting active episode'),
				gmLog.lErr
			)
	#----------------------------------------------
	def _on_patient_selected(self, **kwargs):
		# needed because GUI stuff can't be called from a thread (and that's
		# where we are coming from via backend listener -> dispatcher)
		wxCallAfter(self.__on_patient_selected, **kwargs)
		wxCallAfter(self.__update_allergies, **kwargs)
	#----------------------------------------------
	def __on_patient_selected(self, **kwargs):
		demr = self.curr_pat.get_demographic_record()
		age = demr.getMedicalAge()
		# FIXME: if the age is below, say, 2 hours we should fire
		# a timer here that updates the age in increments of 1 minute ... :-)
		self.txt_age.SetValue(age)
		name = demr.get_names()
		self.patient_selector.SetValue('%s, %s' % (name['last'], name['first']))

		# update episode selector
		self.combo_episodes.Clear()
		epr = self.curr_pat.get_clinical_record()
		if epr is None:
			return None
		episodes = epr.get_episodes()
		for episode in episodes:
			self.combo_episodes.Append(episode['description'], str(episode['pk_episode']))
		self.combo_episodes.SetValue(epr.get_active_episode()['description'])
	#-------------------------------------------------------
	def __on_display_demographics(self, evt):
		print "display patient demographic window now"
	#-------------------------------------------------------
	def _update_allergies(self, **kwargs):
		wxCallAfter(self.__update_allergies)
	#-------------------------------------------------------
	def __update_allergies(self, **kwargs):
		epr = self.curr_pat.get_clinical_record()
		allergies = epr.get_allergies(remove_sensitivities=1)
		if allergies is None:
			self.txt_allergies.SetValue(_('error getting allergies'))
			return False
		if len(allergies) == 0:
			self.txt_allergies.SetValue(_('no allergies recorded'))
			return True
		tmp = []
		for allergy in allergies:
			tmp.append(allergy['descriptor'])
		data = ','.join(tmp)
		self.txt_allergies.SetValue(data)
	#-------------------------------------------------------
	# remote layout handling
	#-------------------------------------------------------
	def AddWidgetRightBottom (self, widget):
		"""Insert a widget on the right-hand side of the bottom toolbar.
		"""
		self.szr_bottom_row.Add(widget, 0, wxRIGHT, 0)
	#-------------------------------------------------------
	def AddWidgetLeftBottom (self, widget):
		"""Insert a widget on the left-hand side of the bottom toolbar.
		"""
		self.szr_bottom_row.Prepend(widget, 0, wxALL, 0)
	#-------------------------------------------------------
	def AddBar (self, key):
		"""Creates and returns a new empty toolbar, referenced by key.

		Key should correspond to the notebook page number as defined
		by the notebook (see gmPlugin.py), so that gmGuiMain can
		display the toolbar with the notebook
		"""
		self.subbars[key] = wxToolBar (
			self.pnl_bottom_row,
			-1,
			size = self.pnl_bottom_row.GetClientSize(),
			style=wxTB_HORIZONTAL | wxNO_BORDER | wxTB_FLAT
		)

		self.subbars[key].SetToolBitmapSize((16,16))
		if len(self.subbars) == 1:
			self.subbars[key].Show(1)
			self.__current = key
		else:
			self.subbars[key].Hide()
		return self.subbars[key]
	#-------------------------------------------------------
	def ReFit (self):
		"""Refits the toolbar after its been changed
		"""
		tw = 0
		th = 0
		# get maximum size for the toolbar
		for i in self.subbars.values ():
			ntw, nth = i.GetSizeTuple ()
			if ntw > tw:
				tw = ntw
			if nth > th:
				th = nth
		#import pdb
		#pdb.set_trace ()
		sz = wxSize (tw, th)
		self.pnl_bottom_row.SetSize(sz)
		for i in self.subbars.values():
			i.SetSize (sz)
		self.szr_main.Layout()
		self.szr_main.Fit(self)
	#-------------------------------------------------------
	def ShowBar (self, key):
		"""Displays the named toolbar.
		"""
		self.subbars[self.__current].Hide()
		try:
			self.subbars[key].Show(1)
			self.__current = key
		except KeyError:
			gmLog.gmDefLog.LogException("cannot show undefined toolbar [%s]" % key, sys.exc_info(), verbose=1)
	#-------------------------------------------------------
	def DeleteBar (self, key):
		"""Removes a toolbar.
		"""
		try:
			self.subbars[key].Destroy()
			del self.subbars[key]
			# FIXME: ??
			if self.__current == key and len(self.subbars):
				self.__current = self.subbars.keys()[0]
				self.subbars[self.__current].Show(1)
		except KeyError:
			gmLog.gmDefLog.LogException("cannot delete undefined toolbar [%s]" % key, sys.exc_info(), verbose=1)

#===========================================================	
if __name__ == "__main__":
	wxInitAllImageHandlers()
	gb = gmGuiBroker.GuiBroker()
	gb['gnumed_dir'] = '..'
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(cMainTopPanel, -1)
	app.MainLoop()
#===========================================================
# $Log: gmTopPanel.py,v $
# Revision 1.47  2004-08-06 09:25:36  ncq
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
