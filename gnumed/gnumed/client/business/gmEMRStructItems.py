"""GnuMed health related business object.

license: GPL
"""
#============================================================
__version__ = "$Revision: 1.22 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"

import types, sys

from Gnumed.pycommon import gmLog, gmPG, gmExceptions
from Gnumed.business import gmClinItem, gmClinNarrative
from Gnumed.pycommon.gmPyCompat import *

import mx.DateTime as mxDT

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cHealthIssue(gmClinItem.cClinItem):
	"""Represents one health issue.
	"""
	_cmd_fetch_payload = """select * from clin_health_issue where id=%s"""

	_cmds_store_payload = [
		"""select 1 from clin_health_issue where id=%(id)s for update""",
		"""update clin_health_issue set
				description=%(description)s
			where id=%(id)s"""
		]

	_updatable_fields = [
		'description'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, patient_id=None, name='xxxDEFAULTxxx'):
		pk = aPK_obj
		if pk is None:
			cmd = "select id from clin_health_issue where id_patient=%s and description=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, patient_id, name)
			if rows is None:
				raise gmExceptions.ConstructorError, 'error getting health issue for [%s:%s]' % (patient_id, name)
			if len(rows) == 0:
				raise gmExceptions.NoSuchClinItemError, 'no health issue for [%s:%s]' % (patient_id, name)
			pk = rows[0][0]
		# instantiate class
		gmClinItem.cClinItem.__init__(self, aPK_obj=pk)
	#--------------------------------------------------------
	def get_patient(self):
		return self._payload[self._idx['id_patient']]
#============================================================
class cEpisode(gmClinItem.cClinItem):
	"""Represents one clinical episode.
	"""
	_cmd_fetch_payload = """select * from v_pat_episodes where pk_episode=%s"""
	_cmds_store_payload = [
		"""select 1 from clin_episode where id=%(id)s for update""",
		"""update clin_episode set
				description=%(description)s,
				fk_health_issue=%(pk_health_issue)s
			where id=%(id)s"""
		]
	_updatable_fields = [
		'description',
		'pk_health_issue'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, id_patient=None, name='xxxDEFAULTxxx'):
		pk = aPK_obj
		if pk is None:
			cmd = "select pk_episode from v_pat_episodes where id_patient=%s and description=%s limit 1"
			rows = gmPG.run_ro_query('historica', cmd, None, id_patient, name)
			if rows is None:
				raise gmExceptions.ConstructorError, 'error getting episode for [%s:%s]' % (id_patient, name)
			if len(rows) == 0:
				raise gmExceptions.NoSuchClinItemError, 'no episode for [%s:%s]' % (id_patient, name)
			pk = rows[0][0]
		# instantiate class
		gmClinItem.cClinItem.__init__(self, aPK_obj=pk)
	#--------------------------------------------------------
	def get_patient(self):
		return self._payload[self._idx['id_patient']]
	#--------------------------------------------------------
	def set_active(self):
		cmd1 = """
			delete from last_act_episode
			where id_patient=(select id_patient from clin_health_issue where id=%s)"""
		cmd2 = """
			insert into last_act_episode(fk_episode, id_patient)
			values (%s,	(select id_patient from clin_health_issue where id=%s))"""
		success, msg = gmPG.run_commit('historica', [
			(cmd1, [self._payload[self._idx['pk_health_issue']]]),
			(cmd2, [self.pk_obj, self._payload[self._idx['pk_health_issue']]])
		], True)
		if not success:
			_log.Log(gmLog.lErr, 'cannot record episode [%s] as most recently used one for health issue [%s]' % (self.pk_obj, self._payload[self._idx['pk_health_issue']]))
			_log.Log(gmLog.lErr, str(msg))
			return False
		return True
#============================================================
class cEncounter(gmClinItem.cClinItem):
	"""Represents one encounter.
	"""
	_cmd_fetch_payload = """
		select * from v_pat_encounters
		where pk_encounter=%s
		"""
	_cmds_store_payload = [
		"""select 1 from clin_encounter where id=%(pk_encounter)s for update""",
		"""update clin_encounter set
				description=%(description)s,
				started=%(started)s,
				last_affirmed=%(last_affirmed)s,
				pk_location=%(pk_location)s,
				pk_provider=%(pk_provider)s,
				pk_type=%(pk_type)s
			where id=%(pk_encounter)s"""
		]

	_updatable_fields = [
		'description',
		'started',
		'last_affirmed',
		'pk_location',
		'pk_provider',
		'pk_type'
	]
	#--------------------------------------------------------
	def set_active(self, staff_id=None):
		"""Set the enconter as the active one.

		"Setting active" means making sure the encounter
		row has the youngest "last_affirmed" timestamp of
		all encounter rows for this patient.

		staff_id - Provider's primary key
		"""
		cmd = """update clin_encounter set
					fk_provider=%s,
					last_affirmed=now()
				where id=%s"""
		success, msg = gmPG.run_commit('historica', [(cmd, [staff_id, self.pk_obj])], True)
		if not success:
			_log.Log(gmLog.lErr, 'cannot reaffirm encounter [%s]' % self.pk_obj)
			_log.Log(gmLog.lErr, str(msg))
			return False
		return True
	#--------------------------------------------------------
	def get_rfes(self):
		"""
            Get RFEs pertinent to this encounter.
		"""
		vals = {'enc': self.pk_obj}
		cmd = """select pk_narrative from v_pat_rfe where pk_encounter=%(enc)s"""
		rows = gmPG.run_ro_query('historica', cmd, None, vals)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot get RFEs for encounter [%s]' % (self.pk_obj))
			return None
		rfes = []
		for row in rows:
		    rfes.append(gmClinNarrative.cRFE(aPK_obj=row[0]))
		return rfes
	#--------------------------------------------------------
	def get_aoes(self):
		"""
            Get AOEs pertinent to this encounter.
		"""
		vals = {'enc': self.pk_obj}
		cmd = """select pk_narrative from v_pat_aoe where pk_encounter=%(enc)s"""
		rows = gmPG.run_ro_query('historica', cmd, None, vals)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot get AOEs for encounter [%s]' % (self.pk_obj))
			return None
		aoes = []
		for row in rows:
		  aoes.append(gmClinNarrative.cAOE(aPK_obj=row[0]))
		return aoes
	#--------------------------------------------------------
	def set_attached_to(self, staff_id=None):
#		"""Attach staff/provider to the encounter.
#
#		staff_id - Staff/provider's primary key
#		"""
#		cmd = """update clin_encounter set fk_provider=%s where id=%s"""
#		success, msg = gmPG.run_commit('historica', [(cmd, [staff_id, self.pk_obj])], True)
#		if not success:
#			_log.Log(gmLog.lErr, 'cannot attach to encounter [%s]' % self.pk_obj)
#			_log.Log(gmLog.lErr, str(msg))
#			return False
#		return True
		pass
#============================================================
# convenience functions
#------------------------------------------------------------	
def create_health_issue(patient_id=None, description='xxxDEFAULTxxx'):
	"""Creates a new health issue for a given patient.

	patient_id - given patient PK
	description - health issue name
	"""
	# already there ?
	try:
		h_issue = cHealthIssue(patient_id=patient_id, name=description)
		return (True, h_issue)
	except gmExceptions.ConstructorError, msg:
		_log.LogException(str(msg), sys.exc_info(), verbose=0)
	# insert new health issue
	queries = []
	cmd = "insert into clin_health_issue (id_patient, description) values (%s, %s)"
	queries.append((cmd, [patient_id, description]))
	# get PK of inserted row
	cmd = "select currval('clin_health_issue_id_seq')"
	queries.append((cmd, []))
	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, msg)
	try:
		h_issue = cHealthIssue(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate health issue [%s]' % (result[0][0]), sys.exc_info, verbose=0)
		return (False, _('internal error, check log'))
	return (True, h_issue)
#-----------------------------------------------------------
def create_episode(id_patient = None, pk_health_issue = None, episode_name='xxxDEFAULTxxx'):
	"""Creates a new episode for a given patient's health issue.

    id_patient - patient PK
	pk_health_issue - given health issue PK
	episode_name - health issue name
	"""
	# already there ?
	try:
		episode = cEpisode(id_patient=id_patient, name=episode_name)
		return (True, episode)
	except gmExceptions.ConstructorError, msg:
		_log.LogException(str(msg), sys.exc_info(), verbose=0)
	# insert new episode
	queries = []
	cmd = "insert into clin_episode (fk_health_issue, description) values (%s, %s)"
	queries.append((cmd, [pk_health_issue, episode_name]))
	# get PK of inserted row
	cmd = "select currval('clin_episode_id_seq')"
	queries.append((cmd, []))
	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, msg)
	try:
		episode = cEpisode(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate episode [%s]' % (result[0][0]), sys.exc_info, verbose=0)
		return (False, _('internal error, check log'))
	return (True, episode)
#-----------------------------------------------------------
def create_encounter(fk_patient=None, fk_location=-1, fk_provider=None, description=None, enc_type=None):
	"""Creates a new encounter for a patient.

	fk_patient - patient PK
	fk_location - encounter location
	fk_provider - who was the patient seen by
	description - name or description for the encounter
	enc_type - type of encounter

	FIXME: we don't deal with location yet
	"""
	# sanity check:
	if description is None:
		description = 'auto-created %s' % mxDT.today().Format('%A %Y-%m-%d %H:%M')
	# FIXME: look for MRU/MCU encounter type here
	if enc_type is None:
		enc_type = 'chart review'
	# insert new encounter
	queries = []
	try:
		enc_type = int(enc_type)
		cmd = """
			insert into clin_encounter (
				fk_patient, fk_location, fk_provider, description, fk_type
			) values (
				%s, -1, %s, %s,	%s
			)"""
	except ValueError:
		enc_type = str(enc_type)
		cmd = """
			insert into clin_encounter (
				fk_patient, fk_location, fk_provider, description, fk_type
			) values (
				%s, -1, %s, %s,	coalesce((select pk from encounter_type where description=%s), 0)
			)"""
	queries.append((cmd, [fk_patient, fk_provider, description, enc_type]))
	cmd = "select currval('clin_encounter_id_seq')"
	queries.append((cmd, []))
	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, msg)
	try:
		encounter = cEncounter(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate encounter [%s]' % (result[0][0]), sys.exc_info, verbose=0)
		return (False, _('internal error, check log'))
	return (True, encounter)
#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	import sys
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')

	print "\nhealth issue test"
	print "-----------------"
	h_issue = cHealthIssue(aPK_obj=1)
	print h_issue
	fields = h_issue.get_fields()
	for field in fields:
		print field, ':', h_issue[field]
	print "updatable:", h_issue.get_updatable_fields()
	

	print "\nepisode test"
	print "------------"
	episode = cEpisode(aPK_obj=1)
	print episode
	fields = episode.get_fields()
	for field in fields:
		print field, ':', episode[field]
	print "updatable:", episode.get_updatable_fields()

	print "\nencounter test"
	print "--------------"
	encounter = cEncounter(aPK_obj=1)
	print encounter
	fields = encounter.get_fields()
	for field in fields:
		print field, ':', encounter[field]
	print "updatable:", encounter.get_updatable_fields()
	rfes = encounter.get_rfes()
	print "rfes: "
	for rfe in rfes:
	    print "\n   rfe test"
	    print "   --------"
	    for field in rfe.get_fields():
	        print '  ', field, ':', rfe[field]
	    print "   updatable:", rfe.get_updatable_fields()
	    
	aoes = encounter.get_aoes()
	for aoe in aoes:
	    print "\n   aoe test"
	    print "   --------"
	    for field in aoe.get_fields():
	        print '  ', field, ':', aoe[field]
	    print "   updatable:", aoe.get_updatable_fields()
	    print "   is diagnosis: " , aoe.is_diagnosis()
	    if aoe.is_diagnosis():
	        print "   diagnosis: ", aoe.get_diagnosis()
	    
#============================================================
# $Log: gmEMRStructItems.py,v $
# Revision 1.22  2004-07-05 10:24:46  ncq
# - use v_pat_rfe/aoe, by Carlos
#
# Revision 1.21  2004/07/04 15:09:40  ncq
# - when refactoring need to fix imports, too
#
# Revision 1.20  2004/07/04 13:24:31  ncq
# - add cRFE/cAOE
# - use in get_rfes(), get_aoes()
#
# Revision 1.19  2004/06/30 20:34:37  ncq
# - cEncounter.get_RFEs()
#
# Revision 1.18  2004/06/26 23:45:50  ncq
# - cleanup, id_* -> fk/pk_*
#
# Revision 1.17  2004/06/26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.16  2004/06/08 00:44:41  ncq
# - v_pat_episodes now has description, not episode for name of episode
#
# Revision 1.15  2004/06/02 22:12:48  ncq
# - cleanup
#
# Revision 1.14  2004/06/02 13:45:19  sjtan
#
# episode->description for update statement as well.
#
# Revision 1.13  2004/06/02 13:18:48  sjtan
#
# revert, as backend view definition was changed yesterday to be more consistent.
#
# Revision 1.12  2004/06/02 12:48:56  sjtan
#
# map episode to description in cursor.description, so can find as episode['description']
# and also save.
#
# Revision 1.11  2004/06/01 23:53:56  ncq
# - v_pat_episodes.episode -> *.description
#
# Revision 1.10  2004/06/01 08:20:14  ncq
# - limit in get_lab_results
#
# Revision 1.9  2004/05/30 20:10:31  ncq
# - cleanup
#
# Revision 1.8  2004/05/22 12:42:54  ncq
# - add create_episode()
# - cleanup add_episode()
#
# Revision 1.7  2004/05/18 22:36:52  ncq
# - need mx.DateTime
# - fix fields updatable in episode
# - fix delete action in episode.set_active()
#
# Revision 1.6  2004/05/18 20:35:42  ncq
# - cleanup
#
# Revision 1.5  2004/05/17 19:02:26  ncq
# - encounter.set_active()
# - improve create_encounter()
#
# Revision 1.4  2004/05/16 15:47:51  ncq
# - add episode.set_active()
#
# Revision 1.3  2004/05/16 14:31:27  ncq
# - cleanup
# - allow health issue to be instantiated by name/patient
# - create_health_issue()/create_encounter
# - based on Carlos' work
#
# Revision 1.2  2004/05/12 14:28:53  ncq
# - allow dict style pk definition in __init__ for multicolum primary keys (think views)
# - self.pk -> self.pk_obj
# - __init__(aPKey) -> __init__(aPK_obj)
#
# Revision 1.1  2004/04/17 12:18:50  ncq
# - health issue, episode, encounter classes
#
