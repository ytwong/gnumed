from wxPython.wx import *
from wxPython.gizmos import *
from wxPython.stc import *
import keyword
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing
                                               #alert messages
import images_gnuMedGP_Toolbar
import gmPlugin
#--------------------------------------------------------------------
# A class for displaying a summary of patients clinical data in the
# form of a social history, family history, active problems, habits
# risk factos and an inbox
# This code is shit and needs fixing, here for gui development only
# TODO:almost everything
#--------------------------------------------------------------------	


ID_OVERVIEW = wxNewId ()
ID_OVERVIEWMENU = wxNewId ()

class ClinicalSummary(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self,parent,id,wxDefaultPosition,wxDefaultSize,style = wxRAISED_BORDER)
	sizer = wxBoxSizer(wxVERTICAL)
	#------------------------------------------------------------------------
	#import social history if available this will be the top item on the page
	#------------------------------------------------------------------------
	try: 
	     import gmGP_SocialHistory
	     socialhistory = gmGP_SocialHistory.SocialHistory(self,-1)
	     
	except:
	     pass
	#------------------------------------------------------------------------
	#import social history if available this will be the top item on the page
	#------------------------------------------------------------------------
        try:                                                      
	     import gmGP_FamilyHistory
	     familyhistory = gmGP_FamilyHistory.FamilyHistory(self,-1)
	     
	except:
	     pass
        #---------------------------------------
	#import active problem list if available 
	#---------------------------------------

	try:                                                        
	     import gmGP_ActiveProblems
	     activeproblemlist = gmGP_ActiveProblems.ActiveProblems(self,-1)
	     
	except:
	     pass	       
	 
	#------------------------------
	#import habits and risk factors
	#------------------------------
        try:                                                        
	     import gmGP_HabitsRiskFactors
	     habitsriskfactors = gmGP_HabitsRiskFactors.HabitsRiskFactors(self,-1)
	     
	except:
	     pass
	
	#------------
	#import inbox
	#------------
        try:                                                        
	     import gmGP_Inbox
	     inbox = gmGP_Inbox.Inbox(self,-1)
	     
	except:
	     pass
	 
	heading1 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Active Problems" )                         
        heading2 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"     Habits            Risk Factors")
	heading3 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Inbox")
        alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,"   Alerts   ")
	#------------------------------------------------------------ 
	#now that we have all the elements, construct the whole panel
	#------------------------------------------------------------
	sizer= wxBoxSizer(wxVERTICAL)
	sizer.Add(socialhistory,5,wxEXPAND)
	sizer.Add(familyhistory,5,wxEXPAND)
	sizer.Add(heading1,0,wxEXPAND)   
	sizer.Add(activeproblemlist,8,wxEXPAND)
	sizer.Add(heading2,0,wxEXPAND)  
	sizer.Add(habitsriskfactors,5,wxEXPAND)
	sizer.Add(heading3,0,wxEXPAND)  
	sizer.Add(inbox,5,wxEXPAND)
	sizer.Add(alertpanel,0,wxEXPAND)
        self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 

class gmGP_ClinicalSummary (gmPlugin.wxBasePlugin):
    """
    Plugin to encapsulate the clinical summary
    """
    def name (self):
        return 'ClinicalSummaryPlugin'

    def register (self):
        self.mwm = self.gb['main.manager']
        self.mwm.RegisterLeftSide ('summary', ClinicalSummary
        (self.mwm, -1))
        tb2 = self.gb['main.bottom_toolbar']
        tb2.AddSeparator()
	tool1 = tb2.AddTool(ID_OVERVIEW, images_gnuMedGP_Toolbar.getToolbar_HomeBitmap(), shortHelpString="Overview of patients records")
	#add a custom separator to the toolbar
	tb2.AddControl(wxStaticBitmap(tb2, -1, images_gnuMedGP_Toolbar.getCustom_SeparatorBitmap(), wxDefaultPosition, wxDefaultSize))
        EVT_TOOL (tb2, ID_OVERVIEW, self.OnSummaryTool)
        self.mwm.SetDefault ('summary')
        menu = self.gb['main.viewmenu']
        menu.Append (ID_OVERVIEWMENU, "S&ummary", "Clinical Summary")
        EVT_MENU (self.gb['main.frame'], ID_OVERVIEWMENU, self.OnSummaryTool)

    def OnSummaryTool (self, event):
        self.mwm.Display ('summary')


if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(ClinicalSummary, -1)
	app.MainLoop()
 
