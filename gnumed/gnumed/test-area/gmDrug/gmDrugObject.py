#!/usr/bin/env python
#############################################################################
#
# gmDrugObject - Object hiding all drug related backend communication
# ---------------------------------------------------------------------------
#
# @author: Hilmar Berger
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
#
# @TODO: Almost everything
############################################################################


#==================================================================             
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/gmDrug/gmDrugObject.py,v $      
__version__ = "$Revision: 1.5 $"                                               
__author__ = "Hilmar Berger <Hilmar.Berger@gmx.net>"

import sys, string, types
import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	# running standalone means diagnostics by definition, hehe
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

import gmCfg
import gmDbObject, gmPG
import gmExceptions
#--------------------------------------------------------------------------
class QueryGroup:
	"""Object holding query strings and associated variable lists grouped together.

	- Every query has to be identified by a unique identifier (string or number).
	- mQueryStrings holds the query strings returning one or more parameters.
	- mVarNames holds a list of variables that are to be filled by the query,
	  for this the order of the returned column names map 1:1 onto the
	  variable names
	- mMappings holds the variables that should be mapped to the query.
    - mInfos holds arbitrary infos (in a single string) about the query.
      This can be used for format strings and so on.
	- These three dictionaries are accessible from other objects.
	- You must use addEntry to add entries to the dictionaries, though, 
	  else the data will be written to the class as static variables.
	"""

	def __init__(self):
		self.mVarNames = {}
		self.mQueryStrings = {}
		self.mMappings = {}

	def addEntry(self, aEntry = None):
		if aEntry != None:
			self.mVarNames[aEntry] = None
			self.mQueryStrings[aEntry] = None
			self.mMappings[aEntry] = None
            
#--------------------------------------------------------------------------
class Drug:
	"""High level API to access drug data"""

	_db = None
	#--------------------------------------------------------------------------
	def __init__(self, fastInit=0, queryCfgSource = None):
		"""initialize static variables"""

		self.mVars = {}    # variables usable for mapping
		self.__mQueryGroups = {}
		self.__mQueryGroupHandlers = {}
		self.__fastInit=0

		# get static database handle if not already initialized by other instance of Drug object
		if Drug._db is None:
			try:
				Drug._db = gmPG.ConnectionPool()
			except:
				exc = sys.exc_info()
				_log.LogException("Failed to initialize ConnectionPool handle.", exc, fatal=1)
				# reraise the exception here
				raise

		# get queries from configuration source (currently only files are supported)
		if queryCfgSource is None:
			_log.Log(gmLog.lWarn, "No query configuration source specified")
			# we want to return an error here 
			# in that case we'll have to raise an exception... can't return
			# anything else than None from an __init__ method
			raise TypeError, "No query configuration source specified"
		else:
			self.__mQueryCfgSource = queryCfgSource
			if not self.__getQueries():
				raise IOError, "cannot load queries"

		# try to fetch all data at once if fastInit is true 
		self.__fastInit = fastInit
		if fastInit:
			self.getAllData()
	#--------------------------------------------------------------------------
	def GetData(self, groupName = None, refresh=0):
		"""Get data of QueryGroupHandlers identified by groupName.

		Returns None if the group does not exist or if the query was not
		successful. Else it returns a dictionary containing all the variables
		defined for this query.
        If the query should be repeated instead of the cached data used, you will
        have to set refresh to 1 (you should do this if some mapped variable was
        changed).
		"""
    	# return None if no sub object was named
		if groupName is None:
			return None

		if self.__mQueryGroupHandlers.has_key(groupName):
			# get query group data
			result = self.__mQueryGroupHandlers[groupName].getData(refresh)
			return result
		else:
			return None
	#--------------------------------------------------------------------------
	def GetAllData(self):
		"""fetch data of all standard sub objects"""
		for s in self.__QueryGroupHandlers.keys():
			self.GetData(s)

	#--------------------------------------------------------------------------
	def __getQueries(self):
		"""get query strings and initialize query group objects"""

		# open configuration source
		try:
			cfgSource = gmCfg.cCfgFile(aFile = self.__mQueryCfgSource)
			# handle all exceptions including 'config file not found'
		except:
			exc = sys.exc_info()
			_log.LogException("Unhandled exception while opening config file [%s]" % self.__mQueryCfgSource, exc, fatal=1)
			return None

		cfgData = cfgSource.getCfg()
		groups = cfgSource.getGroups()

		# every group holds one query consisting of three items: variables, the
		# query itself and the mappings
		# queries are identified by the item 'type=query' 
		for entry_group in groups:
			gtype = cfgSource.get(entry_group, "type")
			# groups not containing queries are silently ignored
			if gtype != 'query':
				continue

			qname = cfgSource.get(entry_group, "querygroup")
			if qname is None:
				_log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
				continue

			qvars = cfgSource.get(entry_group, "variables")
			if qvars is None:
				_log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
				continue

			# query is gonna be a list because of issues
			# with special characters in simple string items
			query = cfgSource.get(entry_group, "query")
			if query is None or not type(query) == types.ListType:
				_log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
				continue
            
			qstring = query[0]

			qmappings = cfgSource.get(entry_group, "mappings")
			if qmappings is None:
				_log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
				continue

			# add new query group to QueryGroups dictionary
			if not self.__mQueryGroups.has_key(qname):
				self.__mQueryGroups[qname] = QueryGroup()
			self.__mQueryGroups[qname].addEntry(entry_group)

			# set the parameters read from config file				
			self.__mQueryGroups[qname].mVarNames[entry_group] = string.split(qvars, ',')
			self.__mQueryGroups[qname].mMappings[entry_group] = string.split(qmappings, ',')
			self.__mQueryGroups[qname].mQueryStrings[entry_group] = qstring

			# inititalize variables used for mapping    	    	
			for v in string.split(qmappings, ','):
				# print "var %s" % v
				if v != '':
					self.mVars[v] = None

		# initialize new QueryGroupHandler objects using configuration data
		for so in self.__mQueryGroups.keys():
			self.__mQueryGroupHandlers[so] = QueryGroupHandler(self, so, self.__mQueryGroups[so])

		return 1
#--------------------------------------------------------------------------
class QueryGroupHandler:
	"""Object covering groups of related items.

	used to access the backend to fetch all those items at once
    """
    #--------------------------------------------------------------------------
	def __init__(self, aParent=None, aName=None, aQueryGroup=None):
		self.__mParent		= None			# points to the parent Drug object, used to access mVars
		self.__mDBObject	= None			# reference to DBObject
		self.__mObjectName	= None			# this DrugQueryGroupHandler's name
		self.__mQueries		= QueryGroup()	# a QueryGroup holding queries to get the data for this QueryGroupHandlers.
		self.__mData		= {}			# a dictionary holding all items belonging to this QueryGroupHandler

		if aParent != None:
			self.__mParent = aParent
		if aQueryGroup != None:
			self.__mQueries = aQueryGroup
		if aName != None:
			self.__mObjectName = aName
	#--------------------------------------------------------------------------
	def getData(self,refresh=0):
		"""returns a dictionary of entry names and its values"""
		
        # if data must be refreshed, clear data cache
		if refresh == 1:
			self.__mData = {}
            
		if len(self.__mData) == 0:
			# if data has not been fetched until now, get the data from backend
			if self.__fetchBackendData():
				return self.__mData
			else:
				return None
		else:             
			# else return the data already available
			return self.__mData
            
	#--------------------------------------------------------------------------
	def __fetchBackendData(self):
		"""try to fetch data from backend"""
		# if no DBObject has been initialized so far, do it now
		if self.__mDBObject is None:
			self.__mDBObject = gmDbObject.DBObject(Drug._db,'pharmaceutica')

		# cycle through query strings and get data
		for queryName in self.__mQueries.mQueryStrings.keys():
			# get variable mappings
			mappings = self.__mQueries.mMappings[queryName]
			allVars = []
			for var in mappings:
				# get variables from parent
				if var != '':
					allVars.append(self.__mParent.mVars[var])

#			print "QUERY ", self.__mQueries.mQueryStrings[queryName] % tuple(allVars)
			# set query string
			if len(allVars) > 0:
				self.__mDBObject.SetSelectQuery(self.__mQueries.mQueryStrings[queryName] % tuple(allVars))
			else:
				self.__mDBObject.SetSelectQuery(self.__mQueries.mQueryStrings[queryName])

			# do the query
			result = self.__mDBObject.Select(listonly=0)

			# maybe we should raise an exception here
			if result is None:
				return None

			# get results
			VarNames = self.__mQueries.mVarNames[queryName]
			VarNumMax = len(VarNames)
			# init missing vars (keys) in data cache dict
			for vn in VarNames:
				if not self.__mData.has_key(vn):
					self.__mData[vn] = []

			# if we got just one row in the result
			if len(result) == 1:
				row = result[0]     # the row we fetched
				col_idx = 0         # column counter
				cols_avail = len(row)   # number of available columns in row
				for col_val in row:     # loop through all columns
					# don't try to map more columns than we have variable name mappings for
					if col_idx > VarNumMax:
						break
					# map column (field) name to variable name in cache object
					VarName = VarNames[col_idx]
					# and cache the value
					self.__mData[VarName] = col_val
                    # increase column count
					col_idx = col_idx + 1

			else:
            	# if multiple rows in result
				for row in result[:]:
					col_idx = 0
					cols_avail = len(row)
					for col_val in row:
						if col_idx > VarNumMax:
							break
						VarName = VarNames[col_idx]
						self.__mData[VarName].append(col_val)
						col_idx = col_idx + 1

		# return TRUE if everything went right
		return 1
#====================================================================================
# MAIN
#====================================================================================

if __name__ == "__main__":
    	import os.path
	tmp = os.path.join(os.path.expanduser("~"), ".gnumed", "amis.conf")
	a = Drug(0, tmp)
	x = a.GetData('brand')
	if x:
		print x
	else:
		print "Query wasn't successful."

	print "-----------------------------------------------------"
	a.mVars['ID']="3337631600"
	y=a.GetData('product_info')
	print y
#	y = a.GetData('brand_all')
#	print y
#	print len(x['brandname'])
#====================================================================================
# $Log: gmDrugObject.py,v $
# Revision 1.5  2002-10-28 23:26:02  hinnef
# first partially functional DrugReferenceBrowser version
#
# Revision 1.4  2002/10/24 13:04:18  ncq
# - just add two silly comments
#
# Revision 1.3  2002/10/23 22:41:54  hinnef
# more cleanup, fixed some bugs regarding variable mapping
#
# Revision 1.2  2002/10/22 21:18:11  ncq
# - fixed massive whitespace lossage
# - sprinkled some comments throughout
# - killed a few levels of indentation
# - tried to rename a few variable to be more self-documenting
#
