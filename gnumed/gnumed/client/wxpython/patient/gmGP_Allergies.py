#############################################################################
# gmGP_Allergies
# --------------
#
# This panel will hold all the allergy details, and allow entry
# of those details via the editing area
#
# If you don't like it - change this code see @TODO!
#
# @author: Dr. Richard Terry
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @TODO:
#	- write gmEditArea.py
#	- decide on type of list and text control to use
#       - someone smart to fix the code (simplify for same result)
#
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/patient/gmGP_Allergies.py,v $
__version__ = "$Revision: 1.23 $"
__author__  = "R.Terry <rterry@gnumed.net>, H.Herb <hherb@gnumed.net>, K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys
#if __name__ == "__main__":
	# FIXME: this will not work on other platforms
	#sys.path.append("../../pycommon")
	#sys.path.append("../../business")
	#sys.path.append("../")

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog

from Gnumed.pycommon import gmDispatcher, gmSignals, gmPG 
from Gnumed.wxpython import gmPlugin_Patient, gmEditArea 
from Gnumed.business import gmPatient

from Gnumed.wxpython import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
from Gnumed.wxpython import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings
from Gnumed.wxpython import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
from Gnumed.wxpython.PatientHolder import PatientHolder
from Gnumed.wxpython import gmPatientHolder
from wxPython.wx import *

ID_ALLERGYLIST = wxNewId()
ID_ALLERGIES = wxNewId ()
ID_ALL_MENU = wxNewId ()
#gmSECTION_ALLERGY = 7

#Dummy data to simulate allergy items
allergydata = {}

#----------------------------------------------------------------------
class AllergyPanel(wxPanel , PatientHolder ):
	def __init__(self, parent,id):
		wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)
		PatientHolder.__init__(self)
		#--------------------
		#add the main heading
		#--------------------
		self.allergypanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self, -1, _("ALLERGIES"))
		#----------------------------------------------
		#now create the editarea specific for allergies
		#----------------------------------------------
#		self.editarea = gmEditArea.EditArea(self, -1, allergyprompts, gmSECTION_ALLERGY)
		self.editarea = gmEditArea.gmAllergyEditArea(self, -1)
		#-----------------------------------------------
		#add the divider headings below the editing area
		#-----------------------------------------------
		self.drug_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Allergy and Sensitivity - Summary"))
		self.sizer_divider_drug_generic = wxBoxSizer(wxHORIZONTAL)
		self.sizer_divider_drug_generic.Add(self.drug_subheading,1, wxEXPAND)
		#--------------------------------------------------------------------------------------
		#add the list to contain the drugs person is allergic to
		#
		# c++ Default Constructor:
		# wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition,
		# const wxSize& size = wxDefaultSize, long style = wxLC_ICON,
		# const wxValidator& validator = wxDefaultValidator, const wxString& name = "listCtrl")
		#
		#--------------------------------------------------------------------------------------
		self.list_allergy = wxListCtrl(self, ID_ALLERGYLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.list_allergy.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		#----------------------------------------
		# add some dummy data to the allergy list
		#----------------------------------------
		self._constructListColumns()
		#-------------------------------------------------------------
		#loop through the scriptdata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.list_allergy.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		#--------------------------------------------------------------------------------------
		#add a richtext control or a wxTextCtrl multiline to display the class text information
		#e.g. would contain say information re the penicillins
		#--------------------------------------------------------------------------------------
		self.classtext_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Class notes for celecoxib")
		self.classtxt = wxTextCtrl(self,-1,
			"A member of a new class of nonsteroidal anti-inflammatory agents (COX-2 selective NSAIDs) which have a mechanism of action that inhibits prostaglandin synthesis primarily by inhibition of cyclooxygenase 2 (COX-2). At therapeutic doses these have no effect on prostanoids synthesised by activation of COX-1 thereby not interfering with normal COX-1 related physiological processes in tissues, particularly the stomach, intestine and platelets.",
			size=(200, 100), style=wxTE_MULTILINE)
		self.classtxt.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		#---------------------------------------------
		#add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(self.allergypanelheading,0,wxEXPAND)
#		self.mainsizer.Add(self.dummypanel,1,wxEXPAND)
		self.mainsizer.Add(self.editarea,6,wxEXPAND)
		self.mainsizer.Add(self.sizer_divider_drug_generic,0,wxEXPAND)
		self.mainsizer.Add(self.list_allergy,5,wxEXPAND)
		self.mainsizer.Add(self.classtext_subheading,0,wxEXPAND)
		self.mainsizer.Add(self.classtxt,4,wxEXPAND)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit
		self.SetAutoLayout(true)
		self.Show(true)

		self.__pat = gmPatient.gmCurrentPatient()
		self.RegisterInterests()
	#-----------------------------------------------
	def RegisterInterests(self):
		gmDispatcher.connect(self.UpdateAllergies, gmSignals.allergy_updated())

		EVT_LIST_ITEM_ACTIVATED( self.list_allergy, self.list_allergy.GetId(), self._allergySelected)
	#-----------------------------------------------

	def _updateUI(self):
		self.UpdateAllergies()

	def _constructListColumns(self):
		self.list_allergy.InsertColumn(0, _("Type"))
		self.list_allergy.InsertColumn(1, _("Status"))
		self.list_allergy.InsertColumn(2, _("Class"))
		self.list_allergy.InsertColumn(3, _("Substance"))
		self.list_allergy.InsertColumn(4, _("Generic"))
		self.list_allergy.InsertColumn(5, _("Reaction"))
		
	
	def _allergySelected(self, event):
		ix = event.GetIndex()
		allergy_map = self.get_allergies().get_allergy_items()
		for id, values in allergy_map.items():
			if ix == 0:
				self.editarea.setInputFieldValues( values, id)
			ix -= 1
			

		

	def _update_list_row( self, i,id,  val_map):
		if val_map['is allergy'] == 1:
			atype = _('allergy')
		else:
			atype = _('sensitivity')
		if val_map['definite']:
			surety = 'definite'
		else:
			surety = 'uncertain'


		self.list_allergy.SetItemData( i, id  )
		self.list_allergy.InsertStringItem( i, atype )
		
		list = [  surety, val_map['allergy class'], val_map['substance'], val_map['generics'], val_map['reaction'] ]
		for j in xrange(0, len( list) ):
			self.list_allergy.SetStringItem( i, j+1, list[j] )
		

	def UpdateAllergies(self, **kwargs):
		# remember wxCallAfter
#		try:
			#epr = self.__pat['clinical record']
			#allergies = epr['allergies']
#			allergy_map = self.get_allergies()
			# { 941: map_values, 2: map_values }
			
#		except:
#			_log.LogException( "problem getting allergy list", sys.exc_info(), 4)
#			return None

#		_log.Data("Allergies " + str(allergy_map))

#		i = 0
#		self.list_allergy.DeleteAllItems()
#		self._constructListColumns()
		
#		for id, val_map in allergy_map.items():
#			self._update_list_row(i, id, val_map)
#			i = i + 1
			
#		for column in range(0,3):
#			self.list_allergy.SetColumnWidth(column, wxLIST_AUTOSIZE)

		return 1

#----------------------------------------------------------------------
class gmGP_Allergies (gmPlugin_Patient.wxPatientPlugin):
	"""Plugin to encapsulate the allergies window"""

	__icons = {
"""icon_letter_A""": 'x\xda\xd3\xc8)0\xe4\nV74S\x00"\x13\x05Cu\xae\xc4`\xf5|\x85d\x05e\x17W\x10\
\x04\xf3\xf5@|77\x03 \x00\xf3\x15\x80|\xbf\xfc\xbcT0\'\x02$i\xee\x06\x82PIT@\
HPO\x0f\xab`\x04\x86\xa0\x9e\x1e\\)\xaa`\x04\x9a P$\x02\xa6\x14Y0\x1f\xa6\
\x14&\xa8\x07\x05h\x82\x11\x11 \xfd\x11H\x82 1\x84[\x11\x82Hn\x85i\x8f\x80\
\xba&"\x82\x08\xbf\x13\x16\xd4\x03\x00\xe4\xa2I\x9c'
}

	def name (self):
		return 'Allergies Window'

	def MenuInfo (self):
		return ('view', '&Allergies')

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[_("""icon_letter_A""")]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_letter_A""")]

	def GetWidget (self, parent):
		return AllergyPanel (parent, -1)

#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(AllergyPanel, -1)
	app.MainLoop()
#============================================================================
# $Log: gmGP_Allergies.py,v $
# Revision 1.23  2004-06-25 13:28:00  ncq
# - logically separate notebook and clinical window plugins completely
#
# Revision 1.22  2004/03/19 21:07:35  shilbert
# - fixed module import
#
# Revision 1.21  2004/02/25 09:46:23  ncq
# - import from pycommon now, not python-common
#
# Revision 1.20  2004/02/05 23:51:01  ncq
# - wxCallAfter() use
#
# Revision 1.19  2003/12/02 02:10:14  ncq
# - comment out stuff so it won't complain, rewrite cleanly eventually !
#
# Revision 1.18  2003/11/23 13:59:10  sjtan
#
# _print removed from base class, so remove debugging calls to it.
#
# Revision 1.17  2003/11/17 10:56:41  sjtan
#
# synced and commiting.
#
# Revision 1.3  2003/10/27 14:01:26  sjtan
#
# syncing with main tree.
#
# Revision 1.2  2003/10/25 08:29:40  sjtan
#
# uses gmDispatcher to send new currentPatient objects to toplevel gmGP_ widgets. Proprosal to use
# yaml serializer to store editarea data in  narrative text field of clin_root_item until
# clin_root_item schema stabilizes.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
# Revision 1.16  2003/11/09 14:52:25  ncq
# - use new API in clinical record
#
# Revision 1.15  2003/10/26 01:36:14  ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.14  2003/06/03 14:28:33  ncq
# - some cleanup, Syans work starts looking good
#
# Revision 1.13  2003/06/01 13:20:32  sjtan
#
# logging to data stream for debugging. Adding DEBUG tags when work out how to use vi
# with regular expression groups (maybe never).
#
# Revision 1.12  2003/06/01 12:55:58  sjtan
#
# sql commit may cause PortalClose, whilst connection.commit() doesnt?
#
# Revision 1.11  2003/06/01 12:46:55  ncq
# - only add pathes if running as main so we don't obscure problems outside this module
#
# Revision 1.10  2003/06/01 01:47:33  sjtan
#
# starting allergy connections.
#
# Revision 1.9  2003/05/21 14:11:26  ncq
# - much needed rewrite/cleanup of gmEditArea
# - allergies/family history edit area adapted to new gmEditArea code
# - old code still there for non-converted edit areas
#
# Revision 1.8  2003/02/02 10:07:58  ihaywood
# bugfix
#
# Revision 1.7  2003/02/02 08:49:49  ihaywood
# demographics being connected to database
#
# Revision 1.6  2003/01/14 20:18:57  ncq
# - fixed setfont() problem
#
# Revision 1.5  2003/01/09 12:01:39  hherb
# connects now to database
#
# @change log:
#	    10.06.2002 rterry initial implementation, untested
#       30.07.2002 rterry images inserted, code cleaned up
