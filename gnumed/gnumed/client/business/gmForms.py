# -*- coding: latin-1 -*-
"""GnuMed forms classes
Business layer for printing all manner of forms, letters, scripts etc.

This code is PROOF OF CONCEPT only
I give no warrant that it will work, or even compile
 
license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmForms.py,v $
# $Id: gmForms.py,v 1.5 2004-03-07 13:19:18 ihaywood Exp $
__version__ = "$Revision: 1.5 $"
__author__ ="Ian Haywood <ihaywood@gnu.org>"
 
import sys, os.path, string, time, re, tempfile, cStringIO, types

# access our modules
#if __name__ == "__main__":
sys.path.append('../..')
 
# start logging
from Gnumed.pycommon import gmLog, gmPG
_log = gmLog.gmDefLog
if __name__ == "__main__":
    _log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)
 
from mx import DateTime
#============================================================

class gmFormEngine:
    """
    Ancestor for forms
    No real functionality as yet
    Descendants should override class variables country, type, electronic, date as neccessary
    """

    def __init__ (self, template, flags=[]):
        self.template = template
        self.flags = flags

    def process (self, params):
        """
        Accept a template [format specific to the engine] and
        dictionary of parameters [specific to the template] for processing into a form.
        Returns a Python file or file-like object representing the
        transmittable form of the form.
        For paper forms, this should be PostScript data or similar.
        """
        pass

    def cleanup (self):
        """
        A sop to TeX which can't act as a true filter to delete temporary files
        """
        pass

    def flags (self):
        """
        A list of flags (true/false options) available in this form instance
        """
        return self.flags

class TextForm (gmFormEngine):
    """
    Takes a plain text form and subsitutes the fields
    which are marked using an escape character.

    The fields are a dictionary of strings or string lists
    If lists, the lines containing these list fields are repeated until one
    of the lists is exhausted.
    """

    def __subst (self, match):
        if self.params.has_key (match): # we have a parameter matching the field
            if type (self.params[match]) is types.ListType:
                self.start_list = 1 # we've got a list, keep repeating this line
                if self.index >= len (self.params[match]):
                    _log.Log (gmLog.lErr, "array field %s exhausted at index %d" % (match, self.index))
                    return ""
                elif len (self.params[match]) == self.index+1: # stop when list exhausted, separate flag so other flags don't overwrite
                    self.stop_list = 1
                return self.params[match][self.index]
            else:
                return self.params[match]
        else:
            _log.Log (gmLog.lInfo, "can't find %s in form dictionary" % match)
            return ""
    
    def process (self, params, escape='@'):
        regex = "%s(\\w+)" % escape
        result = cStringIO.StringIO ()
        self.params = params
        for line in self.template.split ('\n'):
            self.index = 0
            self.start_list = 0
            self.stop_list = 0
            result.write (re.sub (regex, lambda x: self.__subst (x.group (1)), line) + '\n')
            if self.start_list:
                while not self.stop_list:
                    self.index += 1
                    result.write (re.sub (regex, lambda x: self.__subst (x.group (1)), line) + '\n')
        result.seek (0)
        return result
                
                
        
class LaTeXForm (TextForm):
    """
    A forms engine wrapping LaTeX
    """

    def __texify (self, item):
        """
        Convience function to escape strings for TeX output
        """

        if type (item) is types.StringType or type (item) is types.UnicodeType:
            item = item.replace ("\\", "\\backspace")
            item = item.replace ("&", "\\&")
            item = item.replace ("$", "\\$")
            item = item.replace ('"', "")
            item = item.replace ("\n", "\\\\ ")
            if len (item).strip () == 0:
                item = "\relax " # sometimes TeX really hates empty strings, this seems to mollify it
            
            item = item.replace ("� ", "\\\ss\\ ")
            item = item.replace ("�", "\\ss ")
            item = item.replace ("� ", '\\"{a}\\ ')
            item = item.replace ("�", '\\"{a}')
            item = item.replace ("� ", '\\"{A}\\ ')
            item = item.replace ("�", '\\"{A}')
            item = item.replace ("� ", '\\"{o}\\ ')
            item = item.replace ("�", '\\"{o}')
            item = item.replace ("� ", '\\"{O}\\ ')
            item = item.replace ("�", '\\"{O}')
            item = item.replace ("� ", '\\"{u}\\ ')
            item = item.replace ("�", '\\"{u}')
            item = item.replace ("� ", '\\"{U}\\ ')
            item = item.replace ("�", '\\"{U}')
            if type (item) is types.UnicodeType:
                item = item.encode ('ascii') # TeX only works on plain ASCII!
        if type (item) is types.ListType: 
            item = [self.texify (i) for i in item]
        if type (item) is types.IntegerType:
            
        if type (item) is types.DictType:
            for i in item.keys ():
                item[i] = self.texify (i)
        return item

    def process (self, params):
        params = self.__texify (params)
        latex = TextForm.process (self, params)
        # create a 'sandbox' directory for LaTeX to play in
        self.tmp = tempfile.mktemp ()
        os.makedirs (tmp)
        self.oldcwd = os.getcwd ()
        os.chdir (self.tmp)
        stdin = popen ("latex", "w", 2048)
        stdin.write (latex.getvalue ()) # send text. LaTeX spits it's output into stdout.
        # FIXME: send LaTeX  output to the logger
        stdin.close ()
        os.system ("dvips texput.dvi -o texput.ps")
        return file ("texput.ps")

    def xdvi (self):
        """
        For testing purposes
        """
        os.system ("xdvi texput.dvi")

    def cleanup (self):
        for i in os.listdir ('.'):
            os.unlink (i)
        os.chdir (self.oldcwd)
        os.rmdir (self.tmp)

def search_form (discipline, electronic=0):
    """
    Searches for available forms given the discipline and electronicity
    """

    cmd = "select name_short, name_long, version, id from form_types, lnk_form2discipline where id_form = id and discipline like %%s and %s electronic" % (electronic or 'not') and ''
    result = gmPG.run_ro_query ('reference', cmd, None, discipline)
    if result is None:
        return []
    else:
        return [{'name_short':r[0], 'name_long':r[1], 'version':r[2], 'id':r[3]} for r in result]

def get_form (id):
    """
    Instantiates a FormEngine based on the form ID from the backend
    """
    result = gmPG.run_ro_query ('reference', 'select template, engine, flags from form_types where is = %s', None, id)
    if result[1] == 'L':
        return LaTeXForm (result[0], result[2])
    elif result[1] == 'T':
        return TextForm (result[0], result[2])
    else:
        _log.Log (gmLog.lErr, 'no such form engine %s' % result[1])
        return None
    



def test ():
    
    

test ()
