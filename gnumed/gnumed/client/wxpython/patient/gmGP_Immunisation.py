#!/usr/bin/python
#############################################################################
#
# gmGP_Immunisations.py
# ----------------------------------
#
# This panel will hold all the immunisation details
#
# If you don't like it - change this code see @TODO!
#
# @author: Dr. Richard Terry
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	    10.06.2002 rterry initial implementation, untested
#           30.07.2002 rterry icons inserted in file, code cleaned up
# @TODO:
#	
#      
############################################################################

from wxPython.wx import *
import gmGuiElement_HeadingCaptionPanel		#panel class to display top headings
import gmGuiElement_DividerCaptionPanel		#panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel		#panel to hold flashing alert messages
import gmEditArea             				#panel class holding editing prompts and text boxes
import gmPlugin, gmLog

ID_IMMUNISATIONLIST = wxNewId()
ID_IMMUNISATIONS = wxNewId()
ID_ALL_MENU  = wxNewId()

gmSECTION_IMMUNISATIONS = 6
#------------------------------------
#Dummy data to simulate allergy items
#------------------------------------
scheduledata = {
1 : ("Influenza","null"),
2 : ("Tetanus","null"),
3 : ("Typhoid","null"),
}
vaccinedata = {
1 : ("Fluvax","15/03/2001"),
2 : ("Vaxigrip","22/04/2002"),
}

immunisationprompts = {
1:("Target Disease"),
2:("Vaccine"),
3:("Date Given"),
4:("Serial No."),
5:("Site injected"),
6:("Progress Notes"),
7:("")    
}
#----------------------------------------------------------------------
class ImmunisationPanel(wxPanel):

	def __init__(self, parent,id):
		wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)
		#--------------------
		#add the main heading
		#--------------------
		self.immunisationpanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1,_("  IMMUNISATIONS  "))
		#--------------------------------------------
		#dummy panel will later hold the editing area
		#--------------------------------------------
		self.dummypanel1 = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
		self.dummypanel1.SetBackgroundColour(wxColor(222, 222, 222))
		#--------------------------------------------------
		#now create the editarea specific for immunisations
		#--------------------------------------------------
		self.editarea = gmEditArea.EditArea(self,-1,immunisationprompts,gmSECTION_IMMUNISATIONS)
		#-----------------------------------------------
		#add the divider headings below the editing area
		#-----------------------------------------------
		self.disease_schedule_heading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Disease or Schedule"))
		self.vaccine_given_heading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Vaccine Given"))
		self.sizer_divider_schedule_vaccinegiven = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_divider_schedule_vaccinegiven.Add(self.disease_schedule_heading,1, wxEXPAND)
		self.sizer_divider_schedule_vaccinegiven.Add( self.vaccine_given_heading,1, wxEXPAND)
		#--------------------------------------------------------------------------------------
		#add the list to contain the drugs person is allergic to
		#
		# c++ Default Constructor:
		# wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition,
		# const wxSize& size = wxDefaultSize, long style = wxLC_ICON, 
		# const wxValidator& validator = wxDefaultValidator, const wxString& name = "listCtrl")
		#
		#--------------------------------------------------------------------------------------
		self.disease_schedule_list = wxListCtrl(self, ID_IMMUNISATIONLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.disease_schedule_list.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		self.schedule_vaccine_given_list = wxListCtrl(self, ID_IMMUNISATIONLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.schedule_vaccine_given_list.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		self.sizer_schedule_vaccine = wxBoxSizer(wxHORIZONTAL)
		self.sizer_schedule_vaccine.Add(self.disease_schedule_list,4,wxEXPAND)
		self.sizer_schedule_vaccine.Add(self.schedule_vaccine_given_list,6, wxEXPAND)
		#----------------------------------------
		# add some dummy data to the Schedule list
		#-----------------------------------------
		self.disease_schedule_list.InsertColumn(0, _("Schedule"))
		self.disease_schedule_list.InsertColumn(1, "null")
		#-------------------------------------------------------------
		#loop through the scheduledata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.disease_schedule_list.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		items = scheduledata.items()
		for x in range(len(items)):
			key, data = items[x]
			gmLog.gmDefLog.Log (gmLog.lData, items[x])
			self.disease_schedule_list.InsertStringItem(x, data[0])
			self.disease_schedule_list.SetItemData(x, key)

		self.disease_schedule_list.SetColumnWidth(0, wxLIST_AUTOSIZE)
		#-----------------------------------------	  
		# add some dummy data to the vaccines list
		#-----------------------------------------
		self.schedule_vaccine_given_list.InsertColumn(0, _("Vaccine"))
		self.schedule_vaccine_given_list.InsertColumn(1, "null")
		#-------------------------------------------------------------
		#loop through the scheduledata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.disease_schedule_list.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		items = vaccinedata.items()
		for x in range(len(items)):
			key, data = items[x]
			gmLog.gmDefLog.Log (gmLog.lData, items[x])
			self.schedule_vaccine_given_list.InsertStringItem(x, data[0])
			self.schedule_vaccine_given_list.SetStringItem(x, 1, data[1])
			self.schedule_vaccine_given_list.SetItemData(x, key)

		self.schedule_vaccine_given_list.SetColumnWidth(0, wxLIST_AUTOSIZE)
		self.schedule_vaccine_given_list.SetColumnWidth(1, wxLIST_AUTOSIZE)
		#--------------------------------------------------------------------------------------
		#add a richtext control or a wxTextCtrl multiline to display the class text information
		#e.g. would contain say information re the penicillins
		#--------------------------------------------------------------------------------------
		self.missing_immunisations_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Missing Immunisations")
		self.missingimmunisationtxt = wxTextCtrl(self,-1, "Schedule: Pneumococcal - no vaccination recorded",size=(200, 100), style=wxTE_MULTILINE)
		self.missingimmunisationtxt.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		#----------------------------------------
		#add an alert caption panel to the bottom
		#----------------------------------------
		self.alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,"  Alerts  ")
		#---------------------------------------------
		#add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(self.immunisationpanelheading,0,wxEXPAND)
		self.mainsizer.Add(self.dummypanel1,1,wxEXPAND)
		self.mainsizer.Add(self.editarea,6,wxEXPAND)
		self.mainsizer.Add(self.sizer_divider_schedule_vaccinegiven,0,wxEXPAND)
		self.mainsizer.Add( self.sizer_schedule_vaccine,4,wxEXPAND)
		self.mainsizer.Add(self.missing_immunisations_subheading,0,wxEXPAND)
		self.mainsizer.Add(self.missingimmunisationtxt,4,wxEXPAND)
		self.mainsizer.Add(self.alertpanel,0,wxEXPAND)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit (self)
		self.SetAutoLayout(true)
		EVT_SIZE (self, self.OnSize)

	def OnSize (self, event):
		w, h = event.GetSize ()
		self.mainsizer.SetDimension (0, 0, w, h)
#----------------------------------------------------------------------
class gmGP_Immunisation(gmPlugin.wxPatientPlugin):
	"""Plugin to encapsulate the immunisation window."""

	def name (self):
		return 'Immunisations Window'

	def MenuInfo (self):
		return ('view', '&Immunisation')

	def GetIconData(self):
		return 'x\xdam\xd0\xb1\n\x80 \x10\x06\xe0\xbd\xa7\xf8\xa1\xc1\xa6\x9f$\xe8\x01\x1a\
\x1a[Z\\#\x9a\x8a\xea\xfd\xa7N3\xf4\xb0C\x90\xff\xf3\x0e\xd4\xe6\xb8m5\x1b\
\xdbCV\x07k\xaae6\xc4\x8a\xe1X\xd6=$H\x9a\xaes\x0b\xc1I\xa8G\xa9\xb6\x8d\x87\
\xa9H\xa0@\xafe\xa7\xa8Bi\xa2\xdfs$\x19,G:\x175\xa1\x98W\x85\xc1\x9c\x1e\xcf\
Mc4\x85\x9f%\xfc\xae\x93!\xd5K_\xd4\x86\xf8\xa1?\x88\x12\xf9\x00 =F\x87'

	def GetWidget (self, parent):
		return ImmunisationPanel (parent, -1)
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(ImmunisationPanel, -1)
	app.MainLoop()
#----------------------------------------------------------------------
#def getpatient_immunisationsData():
#   return cPickle.loads(zlib.decompress(
#'x\xdam\xd0\xb1\n\x80 \x10\x06\xe0\xbd\xa7\xf8\xa1\xc1\xa6\x9f$\xe8\x01\x1a\
#\x1a[Z\\#\x9a\x8a\xea\xfd\xa7N3\xf4\xb0C\x90\xff\xf3\x0e\xd4\xe6\xb8m5\x1b\
#\xdbCV\x07k\xaae6\xc4\x8a\xe1X\xd6=$H\x9a\xaes\x0b\xc1I\xa8G\xa9\xb6\x8d\x87\
#\xa9H\xa0@\xafe\xa7\xa8Bi\xa2\xdfs$\x19,G:\x175\xa1\x98W\x85\xc1\x9c\x1e\xcf\
#Mc4\x85\x9f%\xfc\xae\x93!\xd5K_\xd4\x86\xf8\xa1?\x88\x12\xf9\x00 =F\x87' ))

#def getpatient_immunisationsBitmap():
#    return wxBitmapFromXPMData(getpatient_immunisationsData())

#def getpatient_immunisationsImage():
#   return wxImageFromBitmap(getpatient_immunisationsBitmap())
