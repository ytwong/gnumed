#!/usr/bin/python
#############################################################################
#
# gmCachedDBObject : abstraction and performance improvement for simple
#                     database query result objects
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: gmPG
# @change log:
#	15.03.2002 hherb first draft, untested
#
# @TODO: Almost everything
############################################################################

# standard Python modules
import copy
# GNUmed modules
import gmLog

class DBcache:

	def __init__(self):
		self.buffer = None
		self.id = None
		self.db = None
		self.querystr = None
		self.lazy = 1	#default: set lazy on
		self.expiry = -1	#default: buffer never expires
		self.lastquery = None	#timestamp of last executed query
		self.notify = {}
		self.attributes = []


class CachedDBObject:

	#static private variables:
	dbcache = DBcache()

	def __init__(self, id=None, db=None, querystr=None, lazy=None, expiry=None):

		#derived classes MUST replace CachedDBObject with their own classname!
		exec("self.cache = %s.dbcache" % self.__class__.__name__)

		self.who = None	#ID for callback function

		if db is not None:
			if self.cache.db is not db:
				self.cache.db = db
				self.reset

		if id is not None:
			self.setId(id)

		if querystr is not None:
			self.setQueryStr(querystr)

		if expiry is not None:
			self.cache.expiry = expiry

		if not lazy and self.cache.buffer is not None:
			self.__query()
		#<DEBUG>
		#_myLog.Log(gmLog.lData, "Instantiated. ID='" + str(self.cache.id) +
		#		"' DB='" + str(self.cache.db) +
		#		"' query='" + str(self.cache.querystr) +
		#		"' lazy='" + str(self.cache.lazy) +
		#		"' expiry='" + str(self.cache.expiry) + "'")
		#</DEBUG>

	def reset(self):
		"force a re-query of buffer on next data access attempt"
		self.cache.buffer = None
		self.cache.lastquery = None

	def setQueryStr(self, querystr):
		if self.cache.querystr != querystr :
			self.cache.querystr = querystr
			self.reset
			_myLog.Log(gmLog.lData, "changing query to SQL>>>" + str(querystr) + "<<<SQL")

	def getQueryStr(self):
		return copy.copy(self.cache.querystr)

	def setId(self, id):
		if self.cache.id != id:
			self.cache.id = id
			self.reset()

	def getId(self):
		"get the ID of the current object"
		return self.cache.id


	def get(self, id=None, copy=1):
		"""returns the buffer. If id is not None and not in cache,
		the backend will be queried."""
		#<DEBUG>
		#print "get called by [%s]" % self.who
		#</DEBUG>
		if id is not None:
			if self.cache.id != id:
				self.cache.id = id
				self.reset()
		if self.cache.buffer is None:
			self.__query()
		if copy:
			try:
				return copy.deepcopy(self.cache.buffer)
			except:
				return self.cache.buffer
		else:
			return self.cache.buffer



	def notify_me(self, who, callback=None):
		"""Register function 'callback' for caller 'who'

		If callback is None, the callback for caller 'who'
		will be removed (if exists)
		'callback' is a function that accepts two parameters:
		The first parameter is the identity of the registered
		caller ('who'), the second parameter is the buffer id.
		'callback' must not return anything"""
		if callback is None:
			try:
				del(self.cache.notify[who])
			except:
				pass
		else:
			self.who = who	#remember who I am
			self.cache.notify[who] = callback


	def notify(self):
		"""forces execution of all registered callback functions
		This function will be called whenever the buffer changes
		"""
		for caller in self.cache.notify.keys():
			#do not notify me if I triggered the query myself
			if caller != self.who:
				self.cache.notify[caller](caller, self.cache.id)
			#<DEBUG>
			#else:
			#	print "Callback function skipped for [%s]" % self.who
			#</DEBUG>


	def attributes(self):
		"returns row attributes ('field names')"
		return self.cache.attributes

	def pprint(self):
		buf = self.get(copy=0)
		#labels = self.attributes()
		pstr=''
		for row in buf:
			for attr in row:
				pstr =  "%s %s | " % (pstr, attr)
			pstr = pstr + "\n"
		return pstr


	def __query(self):
		#<DEBUG>
		#print "%s doing a query" % self.who
		#</DEBUG>
		#assert (self.__cache.__id is not None)
		assert (self.cache.db is not None)
		assert (self.cache.querystr is not None)
		cursor = self.cache.db.cursor()
		#<DEBUG>
		#print "Executing %s\n" % self.cache.querystr
		#</DEBUG>
		cursor.execute(self.cache.querystr)
		self.cache.buffer = cursor.fetchall()
		self.cache.attributes = gmPG.fieldNames(cursor)
		#let everybody know that our buffer has changed
		self.notify()


##############################################################
# convenience only, really
_myLog = gmLog.gmDefLog

if __name__ == "__main__":


	class tables(CachedDBObject):
		dbcache = DBcache()
		def __init__(self, db):
			CachedDBObject.__init__(self, id=-1, db=db, querystr="select * from pg_tables where tablename not like 'pg_%'")

	class dbs(CachedDBObject):
		dbcache = DBcache()
		def __init__(self, db):
			CachedDBObject.__init__(self, id=-1, db=db, querystr="select datname from pg_database")


	#<DEBUG>
	#aHandle = gmLog.LogTargetConsole(gmLog.lData)
	#_myLog.AddTarget(aHandle)
	#</DEBUG>

	def callback(who, id):
		print ">>> Here I am, the callback function! <<<"
		print ">>> My id is %s <<<" % str(id)
		print ">>> I was requested by %s <<<\n" % str(who)

	import gmPG
	conn = gmPG.ConnectionPool()
	db = conn.GetConnection('default')

	#instance of the base class
	databases = CachedDBObject(db=db, id=-1, querystr="select * from pg_database")
	#register callback function for base class instance
	databases.notify_me("main", callback)

	#instances of derived classes
	tablelist = tables(db)
	#dbl and dbl2 share the same buffer, tablelist has it's own as
	#it is derived from a different subclass

	dbl = dbs(db)
	dbl.notify_me("dbl", callback)

	dbl2 = dbs(db)
	dbl2.notify_me("dbl2", callback)

	#databases will now access the backend. No callback should be fired,
	#as there is nobody to share the buffer with.

	dblist = databases.get()
	print "List of available databases:"
	print "-----------------------------------------------------"
	for d in dblist:
		for a in d:
			print str(a) + "\t",
		print "\n"

	print "List of tables in curent database:"
	print "-----------------------------------------------------"
	print tablelist.pprint()

	#now dbl should access the data, and dbl2 should get notified
	#via callback that the buffer has changed

	print "List of databases (names only):"
	print "-----------------------------------------------------"
	print dbl.pprint()

	#just to demonstrate that dbl and dbl2 have not modified
	#the base class buffer
	print "List of databases (all attributes again):"
	print "-----------------------------------------------------"
	print databases.pprint()
	print "-----------------------------------------------------"
	print dbl2.pprint()




