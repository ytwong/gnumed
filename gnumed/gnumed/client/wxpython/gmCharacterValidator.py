
from wxPython.wx import *
import string

		
class CharValidator:
	def __init__(self):
		self.enabled = 1
		self.special_upper = range(192,224)
		self.special_lower = range( 224, 256)
		self.lowercase = range(97, 123) 
		self.uppercase = range(65, 91) 

		self.all_lower = self.lowercase + self.special_lower
		self.all_upper = self.uppercase + self.special_upper

		
		self.digits = range(48, 58)
		self.print_other = range(18, 48) + range( 58 , 65) + range(91, 97) + range(123,126)
		self.print_other.remove(32)
		self.print_other.remove(39)
		self.print_other.remove(45)
		self.name_punctuation = [39, 45]
		


	def setSingleSpace(self, control):
		EVT_CHAR( control, self.allow_single_spaces)

	def setUpperAlpha(self, control):
		EVT_CHAR( control, self.allow_upper_only_exclusive)

	def setCapitalize(self, control):
		EVT_CHAR( control, self.capitalize_exclusive)
			
	def setDigits(self, control):
		EVT_CHAR( control, self.allow_digits_only)

	def allow_single_spaces(self, keyEvent):
		"""wrapper for handling single space input"""
		if self._allow_single_spaces(keyEvent) == 0:
			keyEvent.Skip()
	
	def _allow_single_spaces(self, keyEvent):
		"""intercepts space input and vetos extra spaces.
		returns 1 if intercepted and Skip() was called or 0 if no event was handled.
		"""
		textCtrl = keyEvent.GetEventObject()
		#allow tab to be processed , for navigation
		if keyEvent.GetKeyCode() == WXK_TAB:
			keyEvent.Skip(1)
			return 1

		if keyEvent.GetKeyCode() == WXK_SPACE and ( 
				textCtrl.GetInsertionPoint() == 0
				or textCtrl.GetValue()[textCtrl.GetInsertionPoint()-1] == ' '
				):
			keyEvent.Skip(0)
			return 1
	
		return 0
	
	def allow_upper_only_exclusive(self, keyEvent):
		"""wrapper for converting to upper case and single spaces
		converts intercepts lowercase input and puts in uppercase.
		"""
		print "keyCode=", keyEvent.GetKeyCode()
		if not self._allow_case_only(keyEvent, self.all_lower, self.all_upper, exclusiveof = self.print_other + self.digits):
			keyEvent.Skip()	

	def allow_lower_only(self, keyEvent):
		""" wrapper to convert uppercase to lowercase.
		"""	
		if not  self._allow_case_only( self, keyEvent, self.all_upper, self.all_lower):
			keyEvent.Skip()

	def allow_digits_only( self, keyEvent):

		if self._allow_single_spaces(keyEvent):
			return 

		k = keyEvent.GetKeyCode()
		
		if k in self.all_lower or k in  self.all_upper or k in self.print_other or k in  self.name_punctuation:
			keyEvent.Skip(0)
			return

		keyEvent.Skip(1)
		

	
	def _allow_case_only( self, keyEvent, case, toCase, exclusiveof = []):
		if self._allow_single_spaces(keyEvent):
			return 1

		print "not processed by single space"

		c = keyEvent.GetEventObject()
		
		if keyEvent.GetKeyCode() in case:
			print "in range"
			keyEvent.Skip(0)
			
			p = c.GetInsertionPoint()
			
			print "insertion point =", p, " length of text=", len(c.GetValue())	
			t = c.GetValue()
			u = chr(toCase[case.index(keyEvent.GetKeyCode())]) 	
			print len(t),len(u)
			#wxwidget's initial value bug.
			#t = self._remove_init_whitespace_bug(t)
			c.SetValue(t[:p]+u+t[p:])
			print len(t),len(u)
			print p
			c.SetInsertionPoint(p+1)
			return 1
		
		if exclusiveof <>[] and keyEvent.GetKeyCode()  in exclusiveof:
			keyEvent.Skip(0)
			return 1
		return 0

	def capitalize_exclusive(self, keyEvent):
		if not self._capitalize(keyEvent):
			if  keyEvent.GetKeyCode()  in self.print_other + self.digits :
				keyEvent.Skip(0)
				return
				
			keyEvent.Skip(1)	

	def _remove_init_whitespace_bug(self,t):
			if (t.isspace() and len(t) == 1):
				t = ''
			return t

	def _capitalize(self, keyEvent):
		if self._allow_single_spaces(keyEvent):
			return 1
		k = keyEvent.GetKeyCode()
		if k in self.all_lower:
			keyEvent.Skip(0)
			c = keyEvent.GetEventObject()
			p = c.GetInsertionPoint()
			t = c.GetValue()
			#wxwidget's initial value bug.
			t = self._remove_init_whitespace_bug(t)
			t = t[:p] + chr(k) +t[p:]
			l = t.split(' ')
			l = self.capitalize_list(l)			
					
			t = ' '.join(l)		
					
			c.SetValue(t)
			c.SetInsertionPoint(p+1)
			return 1
		
		return 0
	
	def capitalize_list(self, l):
		for i in xrange(len(l)):
			w = l[i].capitalize()
			if '-' in w:
				l[i] = '-'.join(self.capitalize_list(w.split('-')))

			elif len(w) > 3 and w[:3] == 'Mac':
				l[i] = w[:3] + w[3].upper() + w[4:]
			elif len(w) > 2 and w[:2] == 'Mc':
				l[i] = w[:2] + w[2].upper() + w[3:]
			elif len(w) > 2 and w[1] == "'":
				l[i] = w[:2] + w[2].upper() + w[3:]
			else:
				l[i] =w
		return l
			

if __name__ == "__main__":


	from wxPython.wx import *


	class REWResizer:
		def __init__(self, txtCtrl):
			self.c = txtCtrl
			EVT_TEXT( txtCtrl, txtCtrl.GetId(), self.checkSize)

		def checkSize(self, event):
			#print self.c, self.c.GetNumberOfLines(), self.c.GetTextExtent('A')
			yc = self.c.GetTextExtent('X')[1]
			y = self.c.GetNumberOfLines() * yc
			x0, y0 = self.c.GetClientSizeTuple()
			print y, y0 
			if y > y0 :
				self.c.SetClientSize( (x0, y0 + yc ))
				print "window", self.c.GetId(), "size changed"
				self.adjustParentsChildren(yc)

				c = self.c
				while c <> None:
					if c.GetParent() is None:
						(w,h) = c.GetSizeTuple()
						c.SetSize( (w, h + yc))
						break
					c = c.GetParent()

		def adjustParentsChildren(self, yc):
			c = self.c.GetParent()
			l = c.GetChildren()
			for w in l:
				(x,y) = w.GetPositionTuple()
				if y > self.c.GetPositionTuple()[1]:
					w.SetPosition( ( x, y + yc) )
					

	class REPanel(wxPanel):
		def __init__(self, parent, id):
			wxPanel.__init__(self, parent, id)
			szr1 = wxBoxSizer(wxVERTICAL)
			self.wmap = {}
			self.smap = {}
			#for i in range(0,4):
			#	szr1.AddGrowableRow(i)

			labels = [ 'S', 'O', 'A', 'P' ]
			for i in range(0,4):		
				self.getLine(labels[i],szr1)
			szr1.Add(1,1)
			szr1.Add(1,1)
			self.SetSizer(szr1)
			szr1.Fit(self)
			

		def getLine( self, text, szr):
			szr2 = wxBoxSizer(wxHORIZONTAL)
			szr2.Add(wxStaticText(self, -1, text) )
			#ctrl = wxTextCtrl(self, -1, "")
			ctrl = wxTextCtrl(self, -1, "\n", wxDefaultPosition,
				wxDefaultSize, wxTE_MULTILINE  ) 
			self.wmap[text] = ctrl
			szr2.Add(ctrl, 1, wxGROW )
			self.smap[text] = REWResizer(ctrl) # hold on so not garbage collected
			szr.Add(szr2, 1, wxGROW)
			return szr
			
			
			
					


	class REFrame(wxFrame):
		def __init__(self, parent, id, title):
			wxFrame.__init__(self,parent, id, title)
			self.p = REPanel(self,-1)

	class REApp(wxApp):

		def OnInit(self):
			f = REFrame(None, -1, "Richards XPEditor")	
			f.Show(true)
			f.p.SetSizer(None)
			self.SetTopWindow(f)
			self.f = f
			return true

		def getSOAPMap(self):
			return  self.f.p.wmap
			

	
	app = REApp()
	v = CharValidator()

	m = app.getSOAPMap()
	v.setSingleSpace(m['S'])
	v.setUpperAlpha(m['O'])
	v.setCapitalize(m['A'])
	v.setDigits(m['P'])
	
	
	app.MainLoop()

	
	
