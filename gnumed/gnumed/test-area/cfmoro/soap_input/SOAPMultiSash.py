#----------------------------------------------------------------------
# Name:         multisash
# Purpose:      Multi Sash control
#
# Author:       Gerrit van Dyk
#
# Created:      2002/11/20
# Version:      0.1
# RCS-ID:       $Id: SOAPMultiSash.py,v 1.12 2004-12-03 00:03:32 cfmoro Exp $
# License:      wxWindows licensie
# GnuMed customization (Carlos): 
#		Disabled vertical MultiSizer and MultiCreator (wxMultiViewLeaf)
#		An instance of controller object is passed with DefaultChildClass,
#		to allow problem and emr connection with each SOAP editor control,
#		and also controlling duplicate entries per health issue.
#----------------------------------------------------------------------

from wxPython.wx import *

MV_HOR = 0
MV_VER = not MV_HOR

SH_SIZE = 5 
CR_SIZE = SH_SIZE * 3

import gmSOAPInput

#============================================================
class cSOAPMultiSash(wxWindow):
    """
    Main multisash widget. Dinamically displays a stack of child widgets,
    out SOAP input widgets.
    """
    
    def __init__(self, *_args,**_kwargs):
        apply(wxWindow.__init__,(self,) + _args,_kwargs)
        # SOAP input panel controller object
        self._childController = None
        self.child = None
        self.child = wxMultiSplit(self,self,wxPoint(0,0),self.GetSize())
        EVT_SIZE(self,self.OnMultiSize)

    def SetController(self, childController):
        """
        Set SOAP multisash controller widget. Controller is responsible
        for managing SOAP input widgets lifecycle, control cehcking and
        action handling.
        
        @type childController: gmSOAPInput.cSOAPInputPanel instance
        @param childController: SOAP input panel controller object
        """
        self._childController = childController
        self.child.DefaultChildChanged()	

    def GetController(self):
        """
        Retrieve SOAP input panel controller object
        """
        return self._childController

    def OnMultiSize(self,evt):
        self.child.SetSize(self.GetSize())

    def UnSelect(self):
    	if not self.child is None:
	        self.child.UnSelect()

    def Clear(self):
        self.SetController(None)
        old = self.child
        self.child = wxMultiSplit(self,self,wxPoint(0,0),self.GetSize())
        old.Destroy()
        self.child.OnSize(None)

    def GetSelectedLeaf(self):
        """
        Retrieve currently selected leaf
        """
        return  self.selected_leaf

    def SetSelectedLeaf(self, selected_leaf):
        """
        Set selected leaf
        """
        self.selected_leaf = selected_leaf

#============================================================
class wxMultiSplit(wxWindow):
    """
    Basic split windows container of the multisash widget.
    Has references to two leafs or splitted windows (SOAP input widgets)
    """
    def __init__(self,multiView,parent,pos,size,view1 = None):
        wxWindow.__init__(self,id = -1,parent = parent,pos = pos,size = size,
                          style = wxCLIP_CHILDREN)
                          
        # reference to main multisash widget
        self.multiView = multiView
        self.view2 = None
        if view1:
            self.view1 = view1
            self.view1.Reparent(self)
            self.view1.MoveXY(0,0)
        else:
            self.view1 = wxMultiViewLeaf(self.multiView,self,
                                         wxPoint(0,0),self.GetSize())
        self.direction = None
	
        EVT_SIZE(self,self.OnSize)
	
    def UnSelect(self):
        if self.view1:
            self.view1.UnSelect()
        if self.view2:
            self.view2.UnSelect()

    def DefaultChildChanged(self):
        if not self.view2:
            self.view1.DefaultChildChanged()

    def AddLeaf(self,direction,caller,pos):
        """
        Construct a new leaf (split window, SOAP input widget)
        """
        print "Adding leaf %s %s %s"%(direction, caller, pos)
	    
        # avoid creating duplicate SOAP input widgets for the same issue
        # Leaf creation can be fired both by controller's new button or
        # by leaf's creator element
    	if self.view1.detail.childController.get_selected_issue()[1] in \
            self.view1.detail.childController.get_issues_with_soap():
    		print "Issue has already soap"
    		wx.wxMessageBox("The SOAP note can't be created.\nCurrently selected health issue has yet an associated SOAP note in this encounter.",
                caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION,
                parent = self)
    		return
    	if self.view2:
    	    print "view2"
    	    if caller == self.view1:
                    self.view1 = wxMultiSplit(self.multiView,self,
                                              caller.GetPosition(),
                                              caller.GetSize(),
                                              caller)
                    self.view1.AddLeaf(direction,caller,pos)
            else:
                    self.view2 = wxMultiSplit(self.multiView,self,
                                              caller.GetPosition(),
                                              caller.GetSize(),
                                              caller)
                    self.view2.AddLeaf(direction,caller,pos)
        else:        
    	        if len(self.view1.detail.childController.get_issues_with_soap()) == 0:
    	    	    return
    	        self.direction = direction
                w,h = self.GetSizeTuple()
                if direction == MV_HOR:
                    x,y = (pos,0)
                    w1,h1 = (w-pos,h)
                    w2,h2 = (pos,h)
                else:
                    x,y = (0,pos)
                    w1,h1 = (w,h-pos)
                    w2,h2 = (w,pos)
                self.view2 = wxMultiViewLeaf(self.multiView,self,
                                             wxPoint(x,y),wxSize(w1,h1))
                self.view1.SetSize(wxSize(w2,h2))
                self.view2.OnSize(None)
    
    	        if not self.view1.detail.childController is None:
    	    	    self.view1.detail.childController.check_buttons()

    def DestroyLeaf(self,caller):
        """
        Destroys selected leaf, both by controller's remove button or by
        leaf's destroyer element
        """
        if not self.view2:             
            print "Removing first leaf"
            # we just hide SOAP input widget's contents when removing unique leaf
    	    soap_issue = self.view1.detail.child.GetHealthIssue()
    	    self.view1.detail.child.SetHealthIssue(None)
    	    self.view1.detail.child.ClearSOAP()	    
    	    self.view1.detail.child.HideContents()
    	    if len(self.view1.detail.childController.get_issues_with_soap()) > 0:
    		    self.view1.detail.childController.get_issues_with_soap().remove(soap_issue[1])
    	    self.view1.creatorHor.Hide()
    	    self.view1.closer.Hide()
    	    if not self.view1.detail.childController is None:
    	    	    self.view1.detail.childController.check_buttons()
    	    return                      # we need to destroy any
        parent = self.GetParent()       # Another splitview
        if parent == self.multiView:    # We'r at the root
            if caller == self.view1:
                old = self.view1
                self.view1 = self.view2
                self.view2 = None
                soap_issue = old.detail.child.GetHealthIssue()
                old.detail.childController.get_issues_with_soap().remove(soap_issue[1])
                old.UnSelect()
                old.Destroy()
                print "1.1"
            else:
                soap_issue = self.view2.detail.child.GetHealthIssue()
                self.view2.detail.childController.get_issues_with_soap().remove(soap_issue[1])
                self.view2.UnSelect()
                self.view2.Destroy()
                self.view2 = None
                print "1.2"
            self.view1.SetSize(self.GetSize())
            self.view1.Move(self.GetPosition())
        else:
            w,h = self.GetSizeTuple()
            x,y = self.GetPositionTuple()
            if caller == self.view1:
                if self == parent.view1:
                    parent.view1 = self.view2		    
                else:
                    parent.view2 = self.view2		    
                self.view2.Reparent(parent)
                self.view2.SetDimensions(x,y,w,h)
                print "2.1"
                soap_issue = self.view1.detail.child.GetHealthIssue()
                self.view1.detail.childController.get_issues_with_soap().remove(soap_issue[1])
                print "Removing: %s"%(soap_issue[1])
            else:
                if self == parent.view1:
                    parent.view1 = self.view1
                else:
                    parent.view2 = self.view1
                self.view1.Reparent(parent)
                self.view1.SetDimensions(x,y,w,h)
                print "1.2"
                soap_issue = self.view2.detail.child.GetHealthIssue()
                self.view2.detail.childController.get_issues_with_soap().remove(soap_issue[1])
                print "Removing: %s"%(soap_issue[1])                
            self.view1 = None
            self.view2 = None
	    
            self.Destroy()
            
        #self.multiView.GetController().check_buttons()

    def CanSize(self,side,view):
        if self.SizeTarget(side,view):
            return True
        return False

    def SizeTarget(self,side,view):
        if self.direction == side and self.view2 and view == self.view1:
            return self
        parent = self.GetParent()
        if parent != self.multiView:
            return parent.SizeTarget(side,self)
        return None

    def SizeLeaf(self,leaf,pos,side):
        if self.direction != side:
            return
        if not (self.view1 and self.view2):
            return
        if pos < 10: return
        w,h = self.GetSizeTuple()
        if side == MV_HOR:
            if pos > w - 10: return
        else:
            if pos > h - 10: return
        if side == MV_HOR:
            self.view1.SetDimensions(0,0,pos,h)
            self.view2.SetDimensions(pos,0,w-pos,h)
        else:
            self.view1.SetDimensions(0,0,w,pos)
            self.view2.SetDimensions(0,pos,w,h-pos)

    def OnSize(self,evt):
        if not self.view2:
            self.view1.SetSize(self.GetSize())
            self.view1.OnSize(None)
            return
        v1w,v1h = self.view1.GetSizeTuple()
        v2w,v2h = self.view2.GetSizeTuple()
        v1x,v1y = self.view1.GetPositionTuple()
        v2x,v2y = self.view2.GetPositionTuple()
        w,h = self.GetSizeTuple()

        if v1x != v2x:
            ratio = float(w) / float((v1w + v2w))
            v1w *= ratio
            v2w = w - v1w
            v2x = v1w
        else:
            v1w = v2w = w

        if v1y != v2y:
            ratio = float(h) / float((v1h + v2h))
            v1h *= ratio
            v2h = h - v1h
            v2y = v1h
        else:
            v1h = v2h = h

        self.view1.SetDimensions(v1x,v1y,v1w,v1h)
        self.view2.SetDimensions(v2x,v2y,v2w,v2h)
        self.view1.OnSize(None)
        self.view2.OnSize(None)


#============================================================
class wxMultiViewLeaf(wxWindow):
    """
    A leaf represent a split window, one instance of our SOAP input widget.
    """
    def __init__(self,multiView,parent,pos,size):
        wxWindow.__init__(self,id = -1,parent = parent,pos = pos,size = size,
                          style = wxCLIP_CHILDREN)
                          
        # reference to main multisash widget                  
        self.multiView = multiView
        # only horizontal sizer is allowed, to display leafs in a stack-like way        
        self.sizerHor = MultiSizer(self,MV_HOR)
        self.detail = MultiClient(self, multiView._childController)
        # only horizontal creator is allowed
        self.creatorHor = MultiCreator(self,MV_HOR)
        self.closer = MultiCloser(self)
        # hide creator and closer when a unique leaf is shown
        if multiView._childController is None or \
            len(multiView._childController.get_issues_with_soap()) == 0:
		    self.creatorHor.Hide()
		    self.closer.Hide()

        EVT_SIZE(self,self.OnSize)

    def GetSOAPPanel(self):
        """
        Retrieve split window's SOAP input widget
        """
        return self.detail.child
	
    def UnSelect(self):
        self.detail.UnSelect()

    def DefaultChildChanged(self):
        """
        Set main controller
        """
        self.detail.SetNewController(self.multiView._childController)

    def AddLeaf(self,direction,pos):
        if pos < 10: return
        w,h = self.GetSizeTuple()
        if direction == MV_VER:
            if pos > h - 10: return
        else:
            if pos > w - 10: return
        self.GetParent().AddLeaf(direction,self,pos)

    def DestroyLeaf(self):
        self.GetParent().DestroyLeaf(self)

    def SizeTarget(self,side):
        return self.GetParent().SizeTarget(side,self)

    def CanSize(self,side):
        return self.GetParent().CanSize(side,self)

    def OnSize(self,evt):
        self.sizerHor.OnSize(evt)
        self.creatorHor.OnSize(evt)    
        self.detail.OnSize(evt)
        self.closer.OnSize(evt)

#============================================================
class MultiClient(wxWindow):
    """
    Widget that encapsulate contents in a leaf or split window.
    We have one SOAP input widget and a reference to the controller
    """
    def __init__(self,parent,childController):
        w,h = self.CalcSize(parent)
        wxWindow.__init__(self,id = -1,parent = parent,
                          pos = wxPoint(0,0),
                          size = wxSize(w,h),                          
                          style = wxCLIP_CHILDREN | wxSUNKEN_BORDER)
			  
        print "Creating soap input widget, controller (%s)"%(childController)
        # ui initialized and some issue selection, create SOAP input for the issue
        if not childController is None:
    		self.child = gmSOAPInput.cSOAPControl(self)
    		self.child.SetHealthIssue(childController.get_selected_issue())
    		childController.get_issues_with_soap().append(childController.get_selected_issue()[1])
        else:
		    # empty issue selection 
            self.child = gmSOAPInput.cSOAPControl(self)
		
        self.childController = childController
        self.child.MoveXY(2,2)
        self.normalColour = self.GetBackgroundColour()
        self.Select()

        # empty issue selection, ide unique SOAP input widget
        if childController is None:
		    self.child.HideContents()

        EVT_SET_FOCUS(self,self.OnSetFocus)
        EVT_CHILD_FOCUS(self,self.OnChildFocus)

    def UnSelect(self):
        if self.selected:
            self.selected = False
	    self.GetParent().multiView.SetSelectedLeaf(None)
            self.SetBackgroundColour(self.normalColour)
            self.Refresh()

    def Select(self):    
        self.GetParent().multiView.UnSelect()
        self.GetParent().multiView.SetSelectedLeaf(self.GetParent())
        self.selected = True
        self.SetBackgroundColour(wxColour(255,255,0)) # Yellow
        self.Refresh()
        if not self.childController is None:
            self.childController.check_buttons()

    def CalcSize(self,parent):
        w,h = parent.GetSizeTuple()
        w -= SH_SIZE
        h -= SH_SIZE
        return (w,h)

    def OnSize(self,evt):
        w,h = self.CalcSize(self.GetParent())
        self.SetDimensions(0,0,w,h)
        w,h = self.GetClientSizeTuple()
        self.child.SetSize(wxSize(w-4,h-4))

    def OnSetFocus(self,evt):
        self.Select()
	
    def SetNewController(self,childController):
        """
        Configure main controller
        
        @param: multisash main controller
        @type: gmSOAPInput.cSOAPInputPanel
        """
        self.childController = childController

    def OnChildFocus(self,evt):
        self.OnSetFocus(evt)

#============================================================
class MultiSizer(wxWindow):
    """
    Leaf's sash bar
    """
    def __init__(self,parent,side):
        self.side = side
        x,y,w,h = self.CalcSizePos(parent)
        wxWindow.__init__(self,id = -1,parent = parent,
                          pos = wxPoint(x,y),
                          size = wxSize(w,h),
                          style = wxCLIP_CHILDREN)

        self.px = None                  # Previous X
        self.py = None                  # Previous Y
        self.isDrag = False             # In Dragging
        self.dragTarget = None          # View being sized

        EVT_LEAVE_WINDOW(self,self.OnLeave)
        EVT_ENTER_WINDOW(self,self.OnEnter)
        EVT_MOTION(self,self.OnMouseMove)
        EVT_LEFT_DOWN(self,self.OnPress)
        EVT_LEFT_UP(self,self.OnRelease)

    def CalcSizePos(self,parent):
        pw,ph = parent.GetSizeTuple()
        if self.side == MV_HOR:
            x = CR_SIZE + 2
            y = ph - SH_SIZE
            w = pw - CR_SIZE - SH_SIZE - 2
            h = SH_SIZE
        else:
            x = pw - SH_SIZE
            y = CR_SIZE + 2 + SH_SIZE
            w = SH_SIZE
            h = ph - CR_SIZE - SH_SIZE - 4 - SH_SIZE # For Closer
        return (x,y,w,h)

    def OnSize(self,evt):
        x,y,w,h = self.CalcSizePos(self.GetParent())
        self.SetDimensions(x,y,w,h)

    def OnLeave(self,evt):
        self.SetCursor(wxStockCursor(wxCURSOR_ARROW))

    def OnEnter(self,evt):
        if not self.GetParent().CanSize(not self.side):
            return
        if self.side == MV_HOR:
            self.SetCursor(wxStockCursor(wxCURSOR_SIZENS))
        else:
            self.SetCursor(wxStockCursor(wxCURSOR_SIZEWE))

    def OnMouseMove(self,evt):
        if self.isDrag:
            DrawSash(self.dragTarget,self.px,self.py,self.side)
            self.px,self.py = self.ClientToScreenXY(evt.m_x,evt.m_y)
            self.px,self.py = self.dragTarget.ScreenToClientXY(self.px,self.py)
            DrawSash(self.dragTarget,self.px,self.py,self.side)
        else:
            evt.Skip()

    def OnPress(self,evt):
        self.dragTarget = self.GetParent().SizeTarget(not self.side)
        if self.dragTarget:
            self.isDrag = True
            self.px,self.py = self.ClientToScreenXY(evt.m_x,evt.m_y)
            self.px,self.py = self.dragTarget.ScreenToClientXY(self.px,self.py)
            DrawSash(self.dragTarget,self.px,self.py,self.side)
            self.CaptureMouse()
        else:
            evt.Skip()

    def OnRelease(self,evt):
	if self.isDrag:
            DrawSash(self.dragTarget,self.px,self.py,self.side)
            self.ReleaseMouse()
            self.isDrag = False
            if self.side == MV_HOR:
                self.dragTarget.SizeLeaf(self.GetParent(),
                                         self.py,not self.side)
            else:
                self.dragTarget.SizeLeaf(self.GetParent(),
                                         self.px,not self.side)
            self.dragTarget = None
        else:
            evt.Skip()

#============================================================
class MultiCreator(wxWindow):
    """
    Sash bar's creator element
    """
    def __init__(self,parent,side):
        self.side = side
        x,y,w,h = self.CalcSizePos(parent)
        wxWindow.__init__(self,id = -1,parent = parent,
                          pos = wxPoint(x,y),
                          size = wxSize(w,h),
                          style = wxCLIP_CHILDREN)

        self.px = None                  # Previous X
        self.py = None                  # Previous Y
        self.isDrag = False           # In Dragging

        EVT_LEAVE_WINDOW(self,self.OnLeave)
        EVT_ENTER_WINDOW(self,self.OnEnter)
        EVT_MOTION(self,self.OnMouseMove)
        EVT_LEFT_DOWN(self,self.OnPress)
        EVT_LEFT_UP(self,self.OnRelease)
        EVT_PAINT(self,self.OnPaint)

    def CalcSizePos(self,parent):
        pw,ph = parent.GetSizeTuple()
        if self.side == MV_HOR:
            x = 2
            y = ph - SH_SIZE
            w = CR_SIZE
            h = SH_SIZE
        else:
            x = pw - SH_SIZE
            y = 4 + SH_SIZE             # Make provision for closer
            w = SH_SIZE
            h = CR_SIZE
        return (x,y,w,h)

    def OnSize(self,evt):
        x,y,w,h = self.CalcSizePos(self.GetParent())
        self.SetDimensions(x,y,w,h)

    def OnLeave(self,evt):
        self.SetCursor(wxStockCursor(wxCURSOR_ARROW))

    def OnEnter(self,evt):
        if self.side == MV_HOR:
            self.SetCursor(wxStockCursor(wxCURSOR_HAND))
        else:
            self.SetCursor(wxStockCursor(wxCURSOR_POINT_LEFT))

    def OnMouseMove(self,evt):
        if self.isDrag:
            parent = self.GetParent()
            DrawSash(parent,self.px,self.py,self.side)
            self.px,self.py = self.ClientToScreenXY(evt.m_x,evt.m_y)
            self.px,self.py = parent.ScreenToClientXY(self.px,self.py)
            DrawSash(parent,self.px,self.py,self.side)
        else:
            evt.Skip()

    def OnPress(self,evt):
        self.isDrag = True
        parent = self.GetParent()
        self.px,self.py = self.ClientToScreenXY(evt.m_x,evt.m_y)
        self.px,self.py = parent.ScreenToClientXY(self.px,self.py)
        DrawSash(parent,self.px,self.py,self.side)
        self.CaptureMouse()

    def OnRelease(self,evt):
        print "Released creator"
	if self.isDrag:
            parent = self.GetParent()
            DrawSash(parent,self.px,self.py,self.side)
            self.ReleaseMouse()
            self.isDrag = False

	    if self.side == MV_HOR:
                parent.AddLeaf(MV_VER,self.py)
            else:
                parent.AddLeaf(MV_HOR,self.px)
        else:
            evt.Skip()

    def OnPaint(self,evt):
        dc = wxPaintDC(self)
        dc.SetBackground(wxBrush(self.GetBackgroundColour(),wxSOLID))
        dc.Clear()

        highlight = wxPen(wxSystemSettings_GetSystemColour(
            wxSYS_COLOUR_BTNHIGHLIGHT),1,wxSOLID)
        shadow = wxPen(wxSystemSettings_GetSystemColour(
            wxSYS_COLOUR_BTNSHADOW),1,wxSOLID)
        black = wxPen(wxBLACK,1,wxSOLID)
        w,h = self.GetSizeTuple()
        w -= 1
        h -= 1

        # Draw outline
        dc.SetPen(highlight)
        dc.DrawLine(0,0,0,h)
        dc.DrawLine(0,0,w,0)
        dc.SetPen(black)
        dc.DrawLine(0,h,w+1,h)
        dc.DrawLine(w,0,w,h)
        dc.SetPen(shadow)
        dc.DrawLine(w-1,2,w-1,h)

#============================================================
class MultiCloser(wxWindow):
    """
    Sash bar's destroyer element
    """
    def __init__(self,parent):
        x,y,w,h = self.CalcSizePos(parent)
        wxWindow.__init__(self,id = -1,parent = parent,
                          pos = wxPoint(x,y),
                          size = wxSize(w,h),
                          style = wxCLIP_CHILDREN)

        self.down = False
        self.entered = False

        EVT_LEFT_DOWN(self,self.OnPress)
        EVT_LEFT_UP(self,self.OnRelease)
        EVT_PAINT(self,self.OnPaint)
        EVT_LEAVE_WINDOW(self,self.OnLeave)
        EVT_ENTER_WINDOW(self,self.OnEnter)

    def OnLeave(self,evt):
        self.SetCursor(wxStockCursor(wxCURSOR_ARROW))
        self.entered = False

    def OnEnter(self,evt):
        self.SetCursor(wxStockCursor(wxCURSOR_BULLSEYE))
        self.entered = True

    def OnPress(self,evt):
        self.down = True
        evt.Skip()

    def OnRelease(self,evt):
        if self.down and self.entered:
            self.GetParent().DestroyLeaf()
        else:
            evt.Skip()
        self.down = False

    def OnPaint(self,evt):
        dc = wxPaintDC(self)
        dc.SetBackground(wxBrush(wxRED,wxSOLID))
        dc.Clear()

    def CalcSizePos(self,parent):
        pw,ph = parent.GetSizeTuple()
        x = pw - SH_SIZE
        w = SH_SIZE
        h = SH_SIZE + 2
        y = 1
        return (x,y,w,h)

    def OnSize(self,evt):
        x,y,w,h = self.CalcSizePos(self.GetParent())
        self.SetDimensions(x,y,w,h)


#============================================================
class EmptyChild(wxWindow):
    """
    Empty default widget
    """
    def __init__(self,parent):
        wxWindow.__init__(self,parent,-1, style = wxCLIP_CHILDREN)

#============================================================
def DrawSash(win,x,y,direction):
    """
    Sash drawing method
    """
    
    dc = wxScreenDC()
    dc.StartDrawingOnTopWin(win)
    bmp = wxEmptyBitmap(8,8)
    bdc = wxMemoryDC()
    bdc.SelectObject(bmp)
    bdc.DrawRectangle(-1,-1,10,10)
    for i in range(8):
        for j in range(8):
            if ((i + j) & 1):
                bdc.DrawPoint(i,j)

    brush = wxBrush(wxColour(0,0,0))
    brush.SetStipple(bmp)

    dc.SetBrush(brush)
    dc.SetLogicalFunction(wxXOR)

    body_w,body_h = win.GetClientSizeTuple()

    if y < 0:
        y = 0
    if y > body_h:
        y = body_h
    if x < 0:
        x = 0
    if x > body_w:
        x = body_w

    if direction == MV_HOR:
        x = 0
    else:
        y = 0

    x,y = win.ClientToScreenXY(x,y)

    w = body_w
    h = body_h

    if direction == MV_HOR:
        dc.DrawRectangle(x,y-2,w,4)
    else:
        dc.DrawRectangle(x-2,y,4,h)

    dc.EndDrawingOnTop()
