"""GnuMed vaccination related business objects.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmPathLab.py,v $
# $Id: gmPathLab.py,v 1.5 2004-04-19 12:42:41 ncq Exp $
__version__ = "$Revision: 1.5 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import types

from Gnumed.pycommon import gmLog, gmPG, gmExceptions
from Gnumed.business import gmClinItem
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cLabResult(gmClinItem.cClinItem):
	"""Represents one lab result."""

	_cmd_fetch_payload = """
		select * from v_results4lab_req
		where pk_result=%s"""

	_cmds_store_payload = [
		"""select 1"""
#		"""select 1 from vaccination where id=%(pk_vaccination)s for update""",
#		"""update vaccination set
#				clin_when=%(date)s,
#--				id_encounter
#--				id_episode
#				narrative=%(narrative)s,
#--				fk_patient
#				fk_provider=%(pk_provider)s,
#				fk_vaccine=(select id from vaccine where trade_name=%(vaccine)s),
#				site=%(site)s,
#				batch_no=%(batch_no)s
#			where id=%(pk_vaccination)s"""
		]

	_updatable_fields = [
#		'date',
#		'narrative',
#		'pk_provider',
#		'vaccine',
#		'site',
#		'batch_no'
	]
#============================================================
class cLabRequest(gmClinItem.cClinItem):
	"""Represents one lab request."""

	_cmd_fetch_payload = """
		select * from lab_request
		where pk=%s"""

	_cmds_store_payload = [
		"""select 1 from lab_request where pk=%(pk)s for update""",
		"""update lab_request set
				clin_when=%(clin_when)s,
				narrative=%(narrative)s,
				request_id=%(request_id)s,
				lab_request_id=%(lab_request_id)s,
				lab_rxd_when=%(lab_rxd_when)s,
				results_reported_when=%(results_reported_when)s,
				request_status=%(request_status)s,
				is_pending=%(is_pending)s::bool
			where pk=%(pk)s"""
		]
#--				id_encounter
#--				id_episode

	_updatable_fields = [
		'clin_when',
		'narrative',
		'request_id',
		'lab_request_id',
		'lab_rxd_when',
		'results_reported_when',
		'request_status',
		'is_pending'
	]
	#--------------------------------------------------------
	def __init__(self, aPKey=None, req_id=None, lab=None):
		pk = aPKey
		# no PK given, so find it from req_id and lab
		if pk is None:
			if None in [req_id, lab]:
				raise gmExceptions.ConstructorError, 'req_id and lab must be defined (%s:%s)' % (lab, req_id)
			# generate query
			where_snippets = []
			vals = {}
			where_snippets.append('request_id=%(req_id)s')
			vals['req_id'] = req_id
			if type(lab) == types.IntType:
				where_snippets.append('fk_test_org=%(lab)s')
				vals['lab'] = lab
			else:
				where_snippets.append('fk_test_org=(select pk from test_org where internal_name=%(lab)s)')
				vals['lab'] = str(lab)
			where_clause = ' and '.join(where_snippets)
			cmd = "select pk from lab_request where %s" % where_clause
			data = gmPG.run_ro_query('historica', cmd, None, vals)
			# error
			if data is None:
				raise gmExceptions.ConstructorError, 'error getting lab request for [%s:%s]' % (lab, req_id)
			# no such request
			if len(data) == 0:
				raise gmExceptions.ConstructorError, 'no lab request for [%s:%s]' % (lab, req_id)
			pk = data[0][0]
		# instantiate class
		gmClinItem.cClinItem.__init__(self, aPKey=pk)
#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	def test_result():
		lab_result = cLabResult(aPKey=1)
		print lab_result
		fields = lab_result.get_fields()
		for field in fields:
			print field, ':', lab_result[field]
		print "updatable:", lab_result.get_updatable_fields()
	#--------------------------------------------------------
	def test_request():
#		lab_req = cLabRequest(aPKey=1)
#		lab_req = cLabRequest(req_id='EML#SC937-0176-CEC#11', lab=2)
		lab_req = cLabRequest(req_id='EML#SC937-0176-CEC#11', lab='Enterprise Main Lab')
		print lab_req
		fields = lab_req.get_fields()
		for field in fields:
			print field, ':', lab_req[field]
		print "updatable:", lab_req.get_updatable_fields()
	#--------------------------------------------------------
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')

	test_result()
	test_request()

#============================================================
# $Log: gmPathLab.py,v $
# Revision 1.5  2004-04-19 12:42:41  ncq
# - fix cLabRequest._cms_store_payload
# - modularize testing
#
# Revision 1.4  2004/04/18 18:50:36  ncq
# - override __init__() thusly removing the unholy _pre/post_init() business
#
# Revision 1.3  2004/04/12 22:59:38  ncq
# - add lab request
#
# Revision 1.2  2004/04/11 12:07:54  ncq
# - better unit testing
#
# Revision 1.1  2004/04/11 12:04:55  ncq
# - first version
#
