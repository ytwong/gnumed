# -*- coding: utf-8 -*-
"""Some HL7 handling."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import os
import io
import logging
import time
import shutil
import datetime as pyDT
import hl7 as pyhl7
from xml.etree import ElementTree as pyxml


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain()
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmPathLab
from Gnumed.business import gmPerson
from Gnumed.business import gmStaff


_log = logging.getLogger('gm.hl7')

# constants
HL7_EOL = u'\r'

HL7_SEGMENTS = u'FHS BHS MSH PID PV1 OBX NTE ORC OBR'.split()

HL7_segment2field_count = {
	u'FHS': 12,
	u'BHS': 12,
	u'MSH': 19,
	u'PID': 30,
	u'PV1': 52,
	u'OBR': 43,
	u'OBX': 17,
	u'NTE': 3,
	u'ORC': 19
}

MSH_field__sending_lab = 3

PID_field__name = 5
PID_field__dob = 7
PID_field__gender = 8
PID_component__lastname = 1
PID_component__firstname = 2
PID_component__middlename = 3

OBR_field__service_name = 4
OBR_field__ts_requested = 6
OBR_field__ts_started = 7
OBR_field__ts_ended = 8
OBR_field__ts_specimen_received = 14

OBX_field__set_id = 1
OBX_field__datatype = 2
OBX_field__type = 3
# components of 3rd field:
OBX_component__loinc = 1
OBX_component__name = 2
OBX_field__subid = 4
OBX_field__value = 5
OBX_field__unit = 6
OBX_field__range = 7
OBX_field__abnormal_flag = 8
OBX_field__status = 11
OBX_field__timestamp = 14

NET_field__set_id = 1
NET_field__src = 2
NET_field__note = 3

HL7_field_labels = {
	'MSH': {
		0: 'Segment Type',
		1: 'Field Separator',
		2: 'Encoding Characters',
		3: 'Sending Application',
		4: 'Sending Facility',
		5: 'Receiving Application',
		6: 'Receiving Facility',
		7: 'Date/Time of Message',
		8: 'Security',
		9: 'Message Type',
		10: 'ID: Message Control',
		11: 'ID: Processing',
		12: 'ID: Version',
		14: 'Continuation Pointer',
		15: 'Accept Acknowledgement Type',
		16: 'Application Acknowledgement Type'
	},
	'PID': {
		0: 'Segment Type',
		1: '<PID> Set ID',
		2: 'Patient ID (external)',
		3: 'Patient ID (internal)',
		4: 'Patient ID (alternate)',
		5: 'Patient Name',
		7: 'Date/Time of birth',
		8: 'Administrative Gender',
		11: 'Patient Address',
		13: 'Patient Phone Number - Home'
	},
	'OBR': {
		0: 'Segment Type',
		1: 'ID: Set',
		3: 'Filler Order Number (= ORC-3)',
		4: 'ID: Universal Service',
		5: 'Priority',
		6: 'Date/Time requested',
		7: 'Date/Time Observation started',
		14: 'Date/Time Specimen received',
		16: 'Ordering Provider',
		18: 'Placer Field 1',
		20: 'Filler Field 1',
		21: 'Filler Field 2',
		22: 'Date/Time Results reported/Status changed',
		24: 'ID: Diagnostic Service Section',
		25: 'Result Status',
		27: 'Quantity/Timing',
		28: 'Result Copies To'
	},
	'ORC': {
		0: 'Segment Type',
		1: 'Order Control',
		3: 'Filler Order Number',
		12: 'Ordering Provider'
	},
	'OBX': {
		0: 'Segment Type',
		1: 'Set ID',
		2: 'Value Type',
		3: 'Identifier (LOINC)',
		4: 'Observation Sub-ID',
		5: 'Value',
		6: 'Units',
		7: 'References Range (Low - High)',
		8: 'Abnormal Flags',
		11: 'Result Status',
		14: 'Date/Time of Observation'
	},
	'NTE': {
		0: 'Segment Type',
		3: 'Comment'
	}
}

HL7_GENDERS = {
	u'F': 'f',
	u'M': 'm',
	u'O': None,
	u'U': None,
	None: None
}

#============================================================
# class to handle unmatched incoming clinical data
#------------------------------------------------------------
_SQL_get_incoming_data = u"""SELECT * FROM clin.v_incoming_data_unmatched WHERE %s"""

class cIncomingData(gmBusinessDBObject.cBusinessDBObject):
	"""Represents items of incoming data, say, HL7 snippets."""

	_cmd_fetch_payload = _SQL_get_incoming_data % u"pk_incoming_data_unmatched = %s"
	_cmds_store_payload = [
		u"""UPDATE clin.incoming_data_unmatched SET
				fk_patient_candidates = %(pk_patient_candidates)s,
				fk_identity_disambiguated = %(pk_identity_disambiguated)s,
				fk_provider_disambiguated = %(pk_provider_disambiguated)s,
				request_id = gm.nullify_empty_string(%(request_id)s),
				firstnames = gm.nullify_empty_string(%(firstnames)s),
				lastnames = gm.nullify_empty_string(%(lastnames)s),
				dob = %(dob)s,
				postcode = gm.nullify_empty_string(%(postcode)s),
				other_info = gm.nullify_empty_string(%(other_info)s),
				type = gm.nullify_empty_string(%(data_type)s),
				gender = gm.nullify_empty_string(%(gender)s),
				requestor = gm.nullify_empty_string(%(requestor)s),
				external_data_id = gm.nullify_empty_string(%(external_data_id)s),
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk_incoming_data_unmatched)s
					AND
				xmin = %(xmin_incoming_data_unmatched)s
			RETURNING
				xmin as xmin_incoming_data_unmatched,
				octet_length(data) as data_size
		"""
	]
	# view columns that can be updated:
	_updatable_fields = [
		u'pk_patient_candidates',
		u'request_id',						# request ID as found in <data>
		u'firstnames',
		u'lastnames',
		u'dob',
		u'postcode',
		u'other_info',						# other identifying info in .data
		u'data_type',
		u'gender',
		u'requestor',						# Requestor of data (e.g. who ordered test results) if available in source data.
		u'external_data_id',				# ID of content of .data in external system (e.g. importer) where appropriate
		u'comment',							# a free text comment on this row, eg. why is it here, error logs etc
		u'pk_identity_disambiguated',
		u'pk_provider_disambiguated'		# The provider the data is relevant to.
	]
	#--------------------------------------------------------
	def format(self):
		return u'%s' % self
	#--------------------------------------------------------
	def _format_patient_identification(self):
		tmp = u'%s %s %s' % (
			gmTools.coalesce(self._payload[self._idx['lastnames']], u'', u'last=%s'),
			gmTools.coalesce(self._payload[self._idx['firstnames']], u'', u'first=%s'),
			gmTools.coalesce(self._payload[self._idx['gender']], u'', u'gender=%s')
		)
		if self._payload[self._idx['dob']] is not None:
			tmp += u' dob=%s' % gmDateTime.pydt_strftime(self._payload[self._idx['dob']], '%Y %b %d')
		return tmp

	patient_identification = property(_format_patient_identification, lambda x:x)
	#--------------------------------------------------------
	def update_data_from_file(self, fname=None):
		# sanity check
		if not (os.access(fname, os.R_OK) and os.path.isfile(fname)):
			_log.error('[%s] is not a readable file' % fname)
			return False

		gmPG2.file2bytea (
			query = u"UPDATE clin.incoming_data_unmatched SET data = %(data)s::bytea WHERE pk = %(pk)s",
			filename = fname,
			args = {'pk': self.pk_obj}
		)

		# must update XMIN now ...
		self.refetch_payload()
		return True

	#--------------------------------------------------------
	def export_to_file(self, aChunkSize=0, filename=None):

		if self._payload[self._idx['data_size']] == 0:
			return None

		if self._payload[self._idx['data_size']] is None:
			return None

		if filename is None:
			filename = gmTools.get_unique_filename(prefix = 'gm-incoming_data_unmatched-')

		success = gmPG2.bytea2file (
			data_query = {
				'cmd': u'SELECT substring(data from %(start)s for %(size)s) FROM clin.incoming_data_unmatched WHERE pk = %(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload[self._idx['data_size']]
		)

		if not success:
			return None

		return filename

	#--------------------------------------------------------
	def lock(self, exclusive=False):
		return gmPG2.lock_row(table = u'clin.incoming_data_unmatched', pk = self.pk_obj, exclusive = exclusive)

	#--------------------------------------------------------
	def unlock(self, exclusive=False):
		return gmPG2.unlock_row(table = u'clin.incoming_data_unmatched', pk = self.pk_obj, exclusive = exclusive)

#------------------------------------------------------------
def get_incoming_data(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by
	cmd = _SQL_get_incoming_data % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cIncomingData(row = {'data': r, 'idx': idx, 'pk_field': 'pk_incoming_data_unmatched'}) for r in rows ]

#------------------------------------------------------------
def create_incoming_data(data_type, filename):
	args = {'typ': data_type}
	cmd = u"""
		INSERT INTO clin.incoming_data_unmatched (type, data)
		VALUES (%(typ)s, 'new data'::bytea)
		RETURNING pk"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
	pk = rows[0]['pk']
	incoming = cIncomingData(aPK_obj = pk)
	if not incoming.update_data_from_file(fname = filename):
		delete_incoming_data(incoming_data = pk)
		return None
	return incoming

#------------------------------------------------------------
def delete_incoming_data(pk_incoming_data=None):
	args = {'pk': pk_incoming_data}
	cmd = u"DELETE FROM clin.incoming_data_unmatched WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#============================================================
# public API
#============================================================
def extract_HL7_from_XML_CDATA(filename, xml_path, target_dir=None):

	_log.debug('extracting HL7 from CDATA of <%s> nodes in XML file [%s]', xml_path, filename)

	# sanity checks/setup
	try:
		open(filename).close()
		orig_dir = os.path.split(filename)[0]
		work_filename = gmTools.get_unique_filename(prefix = u'gm-x2h-%s-' % gmTools.fname_stem(filename), suffix = '.hl7')
		if target_dir is None:
			target_dir = os.path.join(orig_dir, u'HL7')
			done_dir = os.path.join(orig_dir, u'done')
		else:
			done_dir = os.path.join(target_dir, u'done')
		_log.debug('target dir: %s', target_dir)
		gmTools.mkdir(target_dir)
		gmTools.mkdir(done_dir)
	except Exception:
		_log.exception('cannot setup unwrapping environment')
		return None

	hl7_xml = pyxml.ElementTree()
	try:
		hl7_xml.parse(filename)
	except pyxml.ParseError:
		_log.exception('cannot parse [%s]' % filename)
		return None
	nodes = hl7_xml.findall(xml_path)
	if len(nodes) == 0:
		_log.debug('no nodes found for data extraction')
		return None

	_log.debug('unwrapping HL7 from XML into [%s]', work_filename)
	hl7_file = io.open(work_filename, mode = 'wt', encoding = 'utf8')
	for node in nodes:
		hl7_file.write(node.text.rstrip(u'\r').rstrip(u'\n').rstrip(u'\r').rstrip(u'\n') + HL7_EOL)
	hl7_file.close()

	target_fname = os.path.join(target_dir, os.path.split(work_filename)[1])
	shutil.copy(work_filename, target_dir)
	shutil.move(filename, done_dir)

	return target_fname

#------------------------------------------------------------
def split_hl7_file(filename, target_dir=None, encoding='utf8'):
	"""Multi-step processing of HL7 files.

	- input can be multi-MSH / multi-PID / partially malformed HL7
	- tries to fix oddities
	- splits by MSH
	- splits by PID into <target_dir>

	- needs write permissions in dir_of(filename)
	- moves HL7 files which were successfully split up into dir_of(filename)/done/

	- returns (True|False, list_of_PID_files)
	"""
	local_log_name = gmTools.get_unique_filename (
		prefix = gmTools.fname_stem(filename) + '-',
		suffix = '.split.log'
	)
	local_logger = logging.FileHandler(local_log_name)
	local_logger.setLevel(logging.DEBUG)
	root_logger = logging.getLogger('')
	root_logger.addHandler(local_logger)
	_log.info('splitting HL7 file: %s', filename)
	_log.debug('log file: %s', local_log_name)

	# sanity checks/setup
	try:
		open(filename).close()
		orig_dir = os.path.split(filename)[0]
		done_dir = os.path.join(orig_dir, u'done')
		gmTools.mkdir(done_dir)
		error_dir = os.path.join(orig_dir, u'failed')
		gmTools.mkdir(error_dir)
		work_filename = gmTools.get_unique_filename(prefix = gmTools.fname_stem(filename) + '-', suffix = '.hl7')
		if target_dir is None:
			target_dir = os.path.join(orig_dir, u'PID')
		_log.debug('target dir: %s', target_dir)
		gmTools.mkdir(target_dir)
	except Exception:
		_log.exception('cannot setup splitting environment')
		root_logger.removeHandler(local_logger)
		return False, None

	# split
	target_names = []
	try:
		shutil.copy(filename, work_filename)
		fixed_filename = __fix_malformed_hl7_file(work_filename, encoding = encoding)
		MSH_fnames = __split_hl7_file_by_MSH(fixed_filename, encoding)
		PID_fnames = []
		for MSH_fname in MSH_fnames:
			PID_fnames.extend(__split_MSH_by_PID(MSH_fname))
		for PID_fname in PID_fnames:
			shutil.move(PID_fname, target_dir)
			target_names.append(os.path.join(target_dir, os.path.split(PID_fname)[1]))
	except Exception:
		_log.exception('cannot split HL7 file')
		for target_name in target_names:
			try: os.remove(target_name)
			except: pass
		root_logger.removeHandler(local_logger)
		shutil.move(local_log_name, error_dir)
		return False, None

	_log.info('successfully split')
	root_logger.removeHandler(local_logger)
	try:
		shutil.move(filename, done_dir)
		shutil.move(local_log_name, done_dir)
	except shutil.Error:
		_log.exception('cannot move hl7 file or log file to holding area')
	return True, target_names

#------------------------------------------------------------
def format_hl7_message(message=None, skip_empty_fields=True, eol=u'\n '):
	# a segment is a line starting with a type
	msg = pyhl7.parse(message)

	output = [[_('HL7 Message'), _(' %s segments (lines)%s') % (len(msg), gmTools.bool2subst(skip_empty_fields, _(', skipping empty fields'), u''))]]

	max_len = 0
	for seg_idx in range(len(msg)):
		seg = msg[seg_idx]
		seg_type = seg[0][0]

		output.append([_('Segment #%s <%s>') % (seg_idx, seg_type), _('%s fields') % len(seg)])

		for field_idx in range(len(seg)):
			field = seg[field_idx]
			try:
				label = HL7_field_labels[seg_type][field_idx]
			except KeyError:
				label = _('HL7 %s field') % seg_type

			max_len = max(max_len, len(label))

			if len(field) == 0:
				if not skip_empty_fields:
					output.append([u'%2s - %s' % (field_idx, label), _('<EMTPY>')])
				continue
			if (len(field) == 1) and ((u'%s' % field[0]).strip() == u''):
				if not skip_empty_fields:
					output.append([u'%2s - %s' % (field_idx, label), _('<EMTPY>')])
				continue

			content_lines = (u'%s' % field).split(u'\.br\\')
			output.append([u'%2s - %s' % (field_idx, label), content_lines[0]])
			for line in content_lines[1:]:
				output.append([u'', line])
			#output.append([u'%2s - %s' % (field_idx, label), u'%s' % field])

	if eol is None:
		return output

	max_len += 7
	return eol.join([ u'%s: %s' % ((o[0] + (u' ' * max_len))[:max_len], o[1]) for o in output ])

#------------------------------------------------------------
def format_hl7_file(filename, skip_empty_fields=True, eol=u'\n ', return_filename=False, fix_hl7=False):
	if fix_hl7:
		fixed_name = __fix_malformed_hl7_file(filename)
		hl7_file = io.open(fixed_name, mode = 'rt', encoding = 'utf8')
	else:
		hl7_file = io.open(filename, mode = 'rt', encoding = 'utf8')
	output = format_hl7_message (
		message = hl7_file.read(1024 * 1024 * 5),		# 5 MB max
		skip_empty_fields = skip_empty_fields,
		eol = eol
	)
	hl7_file.close()

	if not return_filename:
		return output

	if eol is None:
		output = u'\n '.join([ u'%s: %s' % ((o[0] + (u' ' * max_len))[:max_len], o[1]) for o in output ])

	out_name = gmTools.get_unique_filename(prefix = 'gm-formatted_hl7-', suffix = u'.hl7')
	out_file = io.open(out_name, mode = 'wt', encoding = 'utf8')
	out_file.write(output)
	out_file.close()

	return out_name

#------------------------------------------------------------
# this is used in the main code:
def stage_single_PID_hl7_file(filename, source=None, encoding='utf8'):
	"""Multi-step processing of HL7 files.

	- input must be single-MSH / single-PID / normalized HL7

	- imports into clin.incoming_data_unmatched

	- needs write permissions in dir_of(filename)
	- moves PID files which were successfully staged into dir_of(filename)/done/PID/
	"""
	local_log_name = gmTools.get_unique_filename (
		prefix = gmTools.fname_stem(filename) + '-',
		suffix = '.stage.log'
	)
	local_logger = logging.FileHandler(local_log_name)
	local_logger.setLevel(logging.DEBUG)
	root_logger = logging.getLogger('')
	root_logger.addHandler(local_logger)
	_log.info(u'staging [%s] as unmatched incoming HL7%s', filename, gmTools.coalesce(source, u'', u' (%s)'))
	_log.debug(u'log file: %s', local_log_name)

	# sanity checks/setup
	try:
		open(filename).close()
		orig_dir = os.path.split(filename)[0]
		done_dir = os.path.join(orig_dir, u'done')
		gmTools.mkdir(done_dir)
		error_dir = os.path.join(orig_dir, u'failed')
		gmTools.mkdir(error_dir)
	except Exception:
		_log.exception('cannot setup staging environment')
		root_logger.removeHandler(local_logger)
		return False

	# stage
	try:
		inc = create_incoming_data(u'HL7%s' % gmTools.coalesce(source, u'', u' (%s)'), filename)
		if inc is None:
			_log.error(u'cannot stage PID file: %s', filename)
			root_logger.removeHandler(local_logger)
			shutil.move(filename, error_dir)
			shutil.move(local_log_name, error_dir)
			return False
		inc.update_data_from_file(fname = filename)
	except Exception:
		_log.exception(u'error staging PID file')
		root_logger.removeHandler(local_logger)
		shutil.move(filename, error_dir)
		shutil.move(local_log_name, error_dir)
		return False

	# set additional data
	MSH_file = io.open(filename, mode = 'rt', encoding = 'utf8')
	raw_hl7 = MSH_file.read(1024 * 1024 * 5)	# 5 MB max
	MSH_file.close()
	shutil.move(filename, done_dir)
	inc['comment'] = format_hl7_message (
		message = raw_hl7,
		skip_empty_fields = True,
		eol = u'\n'
	)
	HL7 = pyhl7.parse(raw_hl7)
	del raw_hl7
	inc['comment'] += u'\n'
	inc['comment'] += (u'-' * 80)
	inc['comment'] += u'\n\n'
	log = io.open(local_log_name, mode = 'rt', encoding = 'utf8')
	inc['comment'] += log.read()
	log.close()
	try:
		inc['lastnames'] = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__lastname)
		inc['firstnames'] = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__firstname)
		val = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__middlename)
		if val is not None:
			inc['firstnames'] += u' '
			inc['firstnames'] += val
		val = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__dob)
		if val is not None:
			tmp = time.strptime(val, '%Y%m%d')
			inc['dob'] = pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)
		val = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__gender)
		if val is not None:
			inc['gender'] = val
		inc['external_data_id'] = filename
		#u'fk_patient_candidates',
		#	u'request_id',						# request ID as found in <data>
		#	u'postcode',
		#	u'other_info',						# other identifying info in .data
		#	u'requestor',						# Requestor of data (e.g. who ordered test results) if available in source data.
		#	u'fk_identity_disambiguated',
		#	u'comment',							# a free text comment on this row, eg. why is it here, error logs etc
		#	u'fk_provider_disambiguated'		# The provider the data is relevant to.
	except Exception:
		_log.exception(u'cannot add more data')
	inc.save()

	_log.info(u'successfully staged')
	root_logger.removeHandler(local_logger)
	shutil.move(local_log_name, done_dir)
	return True

#------------------------------------------------------------
def process_staged_single_PID_hl7_file(staged_item):

	log_name = gmTools.get_unique_filename (
		prefix = u'gm-staged_hl7_import-',
		suffix = u'.log'
	)
	import_logger = logging.FileHandler(log_name)
	import_logger.setLevel(logging.DEBUG)
	root_logger = logging.getLogger('')
	root_logger.addHandler(import_logger)
	_log.debug('log file: %s', log_name)

	if not staged_item.lock():
		_log.error('cannot lock staged data for HL7 import')
		root_logger.removeHandler(import_logger)
		return False, log_name

	_log.debug('reference ID of staged HL7 data: %s', staged_item['external_data_id'])

	filename = staged_item.export_to_file()
	_log.debug('unstaged HL7 data into: %s', filename)

	if staged_item['pk_identity_disambiguated'] is None:
		emr = None
	else:
		emr = gmPerson.cPatient(staged_item['pk_identity_disambiguated']).emr

	success = False
	try:
		success = __import_single_PID_hl7_file(filename, emr = emr)
		if success:
			delete_incoming_data(pk_incoming_data = staged_item['pk_incoming_data_unmatched'])
			staged_item.unlock()
			root_logger.removeHandler(import_logger)
			return True, log_name
		_log.error('error when importing single-PID/single-MSH file')
	except Exception:
		_log.exception('error when importing single-PID/single-MSH file')

	if not success:
		staged_item['comment'] = _('failed import: %s\n') % gmDateTime.pydt_strftime()
		staged_item['comment'] += u'\n'
		staged_item['comment'] += (u'-' * 80)
		staged_item['comment'] += u'\n\n'
		log = io.open(log_name, mode = 'rt', encoding = 'utf8')
		staged_item['comment'] += log.read()
		log.close()
		staged_item['comment'] += u'\n'
		staged_item['comment'] += (u'-' * 80)
		staged_item['comment'] += u'\n\n'
		staged_item['comment'] += format_hl7_file (
			filename,
			skip_empty_fields = True,
			eol = u'\n ',
			return_filename = False
		)
		staged_item.save()

	staged_item.unlock()
	root_logger.removeHandler(import_logger)
	return success, log_name

#------------------------------------------------------------
def import_single_PID_hl7_file(filename):

	log_name = u'%s.import.log' % filename
	import_logger = logging.FileHandler(log_name)
	import_logger.setLevel(logging.DEBUG)
	root_logger = logging.getLogger('')
	root_logger.addHandler(import_logger)
	_log.debug('log file: %s', log_name)

	success = True
	try:
		success = __import_single_PID_hl7_file(filename)
		if not success:
			_log.error('error when importing single-PID/single-MSH file')
	except Exception:
		_log.exception('error when importing single-PID/single-MSH file')

	root_logger.removeHandler(import_logger)
	return success, log_name

#============================================================
# internal helpers
#============================================================
def __fix_malformed_hl7_file(filename, encoding='utf8'):

	_log.debug(u'fixing HL7 file [%s]', filename)

	# first pass:
	# - remove empty lines
	# - normalize line endings
	# - unwrap wrapped segments
	out1_fname = gmTools.get_unique_filename (
		prefix = u'gm_fix1-%s-' % gmTools.fname_stem(filename),
		suffix = u'.hl7'
	)
	hl7_in = io.open(filename, mode = 'rt', encoding = encoding)
	hl7_out = io.open(out1_fname, mode = 'wt', encoding = 'utf8')

	is_first_line = True
	for line in hl7_in:
		# skip empty line
		if line.strip().strip(u'\r').strip(u'\n').strip(u'\r').strip(u'\n').strip() == u'':
			continue

		# starts with known segment ?
		segment = line[:3]
		if (segment in HL7_SEGMENTS) and (line[3] == u'|'):
			if not is_first_line:
				hl7_out.write(HL7_EOL)
			else:
				is_first_line = False

		hl7_out.write(line.rstrip(u'\r').rstrip(u'\n').rstrip(u'\r').rstrip(u'\n'))

	hl7_out.close()
	hl7_in.close()

	# second pass:
	# - normalize # of fields per line
	out2_fname = gmTools.get_unique_filename (
		prefix = u'gm_fix2-%s-' % gmTools.fname_stem(filename),
		suffix = '.hl7'
	)
	hl7_in = io.open(out1_fname, mode = 'rt', encoding = 'utf8')
	hl7_out = io.open(out2_fname, mode = 'wt', encoding = 'utf8')

	for line in hl7_in:
		line = line.strip(HL7_EOL)
		seg_type = line[:3]						# assumption: field separator = '|'
		field_count = line.count(u'|') + 1		# assumption: no '|' in data ...
		try:
			required_fields = HL7_segment2field_count[seg_type]
		except KeyError:
			required_fields = field_count
		missing_fields_count = required_fields - field_count
		if missing_fields_count > 0:
			line += (u'|' * missing_fields_count)
		hl7_out.write(line + HL7_EOL)

	hl7_out.close()
	hl7_in.close()

	# third pass:
	# - unsplit same-name, same-time, text-type OBX segments
	out3_fname = gmTools.get_unique_filename (
		prefix = u'gm_fix3-%s-' % gmTools.fname_stem(filename),
		suffix = '.hl7'
	)
	hl7_in = io.open(out2_fname, mode = 'rt', encoding = 'utf8')
	hl7_out = io.open(out3_fname, mode = 'wt', encoding = 'utf8')

	prev_identity = None
	prev_fields = None
	for line in hl7_in:
		if not line.startswith(u'OBX|'):
			if prev_fields is not None:
				hl7_out.write(u'|'.join(prev_fields) + HL7_EOL)
			hl7_out.write(line)
			prev_identity = None
			prev_fields = None
			curr_fields = None
			continue
		line = line.strip(HL7_EOL)
		# first OBX
		curr_fields = line.split(u'|')
		if curr_fields[OBX_field__datatype] != u'FT':
			hl7_out.write(line + HL7_EOL)
			prev_identity = None
			prev_fields = None
			curr_fields = None
			continue
		# first FT type OBX
		if prev_fields is None:
			prev_fields = line.split(u'|')
			prev_identity = line.split(u'|')
			prev_identity[OBX_field__set_id] = u''
			prev_identity[OBX_field__subid] = u''
			prev_identity[OBX_field__value] = u''
			prev_identity = u'|'.join(prev_identity)
			continue
		# non-first FT type OBX
		curr_identity = line.split(u'|')
		curr_identity[OBX_field__set_id] = u''
		curr_identity[OBX_field__subid] = u''
		curr_identity[OBX_field__value] = u''
		curr_identity = u'|'.join(curr_identity)
		if curr_identity != prev_identity:
			# write out previous line
			hl7_out.write(u'|'.join(prev_fields) + HL7_EOL)
			# keep current fields, since it may start a "repeat FT type OBX block"
			prev_fields = curr_fields
			prev_identity = curr_identity
			continue
		if prev_fields[OBX_field__value].endswith(u'\.br\\'):
			prev_fields[OBX_field__value] += curr_fields[OBX_field__value]
		else:
			if curr_fields[OBX_field__value].startswith(u'\.br\\'):
				prev_fields[OBX_field__value] += curr_fields[OBX_field__value]
			else:
				prev_fields[OBX_field__value] += u'\.br\\'
				prev_fields[OBX_field__value] += curr_fields[OBX_field__value]

	if prev_fields is not None:
		hl7_out.write(u'|'.join(prev_fields) + HL7_EOL)

	hl7_out.close()
	hl7_in.close()

	return out3_fname

#------------------------------------------------------------
def __split_hl7_file_by_MSH(filename, encoding='utf8'):

	_log.debug('splitting [%s] into single-MSH files', filename)

	hl7_in = io.open(filename, mode = 'rt', encoding = encoding)

	idx = 0
	first_line = True
	MSH_file = None
	MSH_fnames = []
	for line in hl7_in:
		# first line must be MSH
		if first_line:
			# ignore empty / FHS / BHS lines
			if line.strip() == u'':
				continue
			if line.startswith(u'FHS|'):
				_log.debug('ignoring FHS')
				continue
			if line.startswith(u'BHS|'):
				_log.debug('ignoring BHS')
				continue
			if not line.startswith(u'MSH|'):
				raise ValueError('HL7 file <%s> does not start with "MSH" line' % filename)
			first_line = False
		# start new file
		if line.startswith(u'MSH|'):
			if MSH_file is not None:
				MSH_file.close()
			idx += 1
			out_fname = gmTools.get_unique_filename(prefix = u'%s-MSH_%s-' % (gmTools.fname_stem(filename), idx), suffix = 'hl7')
			_log.debug('writing message %s to [%s]', idx, out_fname)
			MSH_fnames.append(out_fname)
			MSH_file = io.open(out_fname, mode = 'wt', encoding = 'utf8')
		# ignore BTS / FTS lines
		if line.startswith(u'BTS|'):
			_log.debug('ignoring BTS')
			continue
		if line.startswith(u'FTS|'):
			_log.debug('ignoring FTS')
			continue
		# else write line to new file
		MSH_file.write(line.strip('\n').strip('\r').strip('\n').strip('\r') + HL7_EOL)

	if MSH_file is not None:
		MSH_file.close()
	hl7_in.close()

	return MSH_fnames

#------------------------------------------------------------
def __split_MSH_by_PID(filename):
	"""Assumes:
		- ONE MSH per file
		- utf8 encoding
		- first non-empty line must be MSH line
		- next line must be PID line

		IOW, what's created by __split_hl7_file_by_MSH()
	"""
	_log.debug('splitting single-MSH file [%s] into single-PID files', filename)

	MSH_in = io.open(filename, mode = 'rt', encoding = 'utf8')

	looking_for_MSH = True
	MSH_line = None
	looking_for_first_PID = True
	PID_file = None
	PID_fnames = []
	idx = 0
	for line in MSH_in:
		# ignore empty
		if line.strip() == u'':
			continue

		# first non-empty line must be MSH
		if looking_for_MSH:
			if line.startswith(u'MSH|'):
				looking_for_MSH = False
				MSH_line = line.strip('\n').strip('\r').strip('\n').strip('\r') + u'\r'
				continue
			raise ValueError('HL7 MSH file <%s> does not start with "MSH" line' % filename)
		else:
			if line.startswith(u'MSH|'):
				raise ValueError('HL7 single-MSH file <%s> contains more than one MSH line' % filename)

		# first non-empty line after MSH must be PID
		if looking_for_first_PID:
			if not line.startswith(u'PID|'):
				raise ValueError('HL7 MSH file <%s> does not have "PID" line follow "MSH" line' % filename)
			looking_for_first_PID = False

		# start new file if line is PID
		if line.startswith(u'PID|'):
			if PID_file is not None:
				PID_file.close()
			idx += 1
			out_fname = gmTools.get_unique_filename(prefix = u'%s-PID_%s-' % (gmTools.fname_stem(filename), idx), suffix = 'hl7')
			_log.debug('writing message for PID %s to [%s]', idx, out_fname)
			PID_fnames.append(out_fname)
			PID_file = io.open(out_fname, mode = 'wt', encoding = 'utf8')
			PID_file.write(MSH_line)
		# else write line to new file
		PID_file.write(line.strip('\n').strip('\r').strip('\n').strip('\r') + HL7_EOL)

	if PID_file is not None:
		PID_file.close()
	MSH_in.close()

	return PID_fnames

#------------------------------------------------------------
def __find_or_create_lab(hl7_lab, link_obj=None):
	comment_tag = u'[HL7 name::%s]' % hl7_lab
	for gm_lab in gmPathLab.get_test_orgs():
		if comment_tag in gmTools.coalesce(gm_lab['comment'], u''):
			_log.debug('found lab [%s] from HL7 file in GNUmed database:', hl7_lab)
			_log.debug(gm_lab)
			return gm_lab
	_log.debug('lab not found: %s', hl7_lab)
	gm_lab = gmPathLab.create_test_org(link_obj = link_obj, name = hl7_lab, comment = comment_tag)
	if gm_lab is None:
		raise ValueError('cannot create lab [%s] in GNUmed' % hl7_lab)
	_log.debug('created lab: %s', gm_lab)
	return gm_lab

#------------------------------------------------------------
def __find_or_create_test_type(loinc=None, name=None, pk_lab=None, unit=None, link_obj=None, abbrev=None):

	tt = gmPathLab.find_measurement_type(link_obj = link_obj, lab = pk_lab, name = name)
	if tt is None:
		_log.debug('test type [%s %s (%s)] not found for lab #%s, creating', name, unit, loinc, pk_lab)
		tt = gmPathLab.create_measurement_type(link_obj = link_obj, lab = pk_lab, abbrev = gmTools.coalesce(abbrev, name), unit = unit, name = name)

	if loinc is None:
		return tt
	if loinc.strip() == u'':
		return tt
	if tt['loinc'] is None:
		tt['loinc'] = loinc
		tt.save(conn = link_obj)
		return tt
	if tt['loinc'] != loinc:
#		raise ValueError('LOINC code mismatch between GM (%s) and HL7 (%s) for result type [%s]' % (tt['loinc'], loinc, name))
		_log.error('LOINC code mismatch between GM (%s) and HL7 (%s) for result type [%s]', tt['loinc'], loinc, name)

	return tt

#------------------------------------------------------------
def __ensure_hl7_test_types_exist_in_gnumed(link_obj=None, hl7_data=None, pk_test_org=None):
	try:
		OBX_count = len(hl7_data.segments('OBX'))
	except KeyError:
		_log.error("HL7 does not contain OBX segments, nothing to do")
		return
	for OBX_idx in range(OBX_count):
		unit = hl7_data.extract_field(segment = u'OBX', segment_num = OBX_idx, field_num = OBX_field__unit)
		if unit == u'':
			unit = None
		LOINC = hl7_data.extract_field(segment = u'OBX', segment_num = OBX_idx, field_num = OBX_field__type, component_num = OBX_component__loinc)
		tname = hl7_data.extract_field(segment = u'OBX', segment_num = OBX_idx, field_num = OBX_field__type, component_num = OBX_component__name)
		tt = __find_or_create_test_type (
			loinc = LOINC,
			name = tname,
			pk_lab = pk_test_org,
			unit = unit,
			link_obj = link_obj
		)

#------------------------------------------------------------
def __PID2dto(HL7=None):
	pat_lname = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__lastname)
	pat_fname = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__firstname)
	pat_mname = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__middlename)
	if pat_mname is not None:
		pat_fname += u' '
		pat_fname += pat_mname
	_log.debug(u'patient data from PID segment: first=%s (middle=%s) last=%s', pat_fname, pat_mname, pat_lname)

	dto = gmPerson.cDTO_person()
	dto.firstnames = pat_fname
	dto.lastnames = pat_lname
	dto.gender = HL7_GENDERS[HL7.extract_field('PID', segment_num = 1, field_num = PID_field__gender)]
	hl7_dob = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__dob)
	if hl7_dob is not None:
		tmp = time.strptime(hl7_dob, '%Y%m%d')
		dto.dob = pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)

	idents = dto.get_candidate_identities()
	if len(idents) == 0:
		_log.warning('no match candidate, not auto-importing')
		_log.debug(dto)
		return []
	if len(idents) > 1:
		_log.warning('more than one match candidate, not auto-importing')
		_log.debug(dto)
		return idents
	return [gmPerson.cPatient(idents[0].ID)]

#------------------------------------------------------------
def __hl7dt2pydt(hl7dt):
	if hl7dt == u'':
		return None

	if len(hl7dt) == 8:
		tmp = time.strptime(hl7dt, '%Y%m%d')
		return pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)

	if len(hl7dt) == 12:
		tmp = time.strptime(hl7dt, '%Y%m%d%H%M')
		return pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tmp.tm_hour, tmp.tm_min, tzinfo = gmDateTime.gmCurrentLocalTimezone)

	if len(hl7dt) == 14:
		tmp = time.strptime(hl7dt, '%Y%m%d%H%M%S')
		return pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tmp.tm_hour, tmp.tm_min, tmp.tm_sec, tzinfo = gmDateTime.gmCurrentLocalTimezone)

	raise ValueError('Observation timestamp not parseable: [%s]', hl7dt)

#------------------------------------------------------------
def __import_single_PID_hl7_file(filename, emr=None):
	"""Assumes single-PID/single-MSH HL7 file."""

	_log.debug('importing single-PID single-MSH HL7 data from [%s]', filename)

	# read the file
	MSH_file = io.open(filename, mode = 'rt', encoding = 'utf8')
	HL7 = pyhl7.parse(MSH_file.read(1024 * 1024 * 5))	# 5 MB max
	MSH_file.close()

	# sanity checks
	if len(HL7.segments('MSH')) != 1:
		_log.error('more than one MSH segment')
		return False
	if len(HL7.segments('PID')) != 1:
		_log.error('more than one PID segment')
		return False

	# ensure lab is in database
	hl7_lab = HL7.extract_field('MSH', field_num = MSH_field__sending_lab)
	gm_lab = __find_or_create_lab(hl7_lab)

	# ensure test types exist
	conn = gmPG2.get_connection(readonly = False)
	__ensure_hl7_test_types_exist_in_gnumed(link_obj = conn, hl7_data = HL7, pk_test_org = gm_lab['pk_test_org'])

	# find patient
	if emr is None:
		#PID = HL7.segment('PID')
		pats = __PID2dto(HL7 = HL7)
		if len(pats) == 0:
			conn.rollback()
			return False
		if len(pats) > 1:
			conn.rollback()
			return False
		emr = pats[0].emr

	# import values: loop over segments
	when_list = {}
	current_result = None
	previous_segment = None
	had_errors = False
	msh_seen = False
	pid_seen = False
	last_obr = None
	obr = {}
	for seg_idx in range(len(HL7)):
		seg = HL7[seg_idx]
		seg_type = seg[0][0]

		_log.debug('processing line #%s = segment of type <%s>', seg_idx, seg_type)

		if seg_type == u'MSH':
			msh_seen = True

		if seg_type == u'PID':
			if not msh_seen:
				conn.rollback()
				_log.error('PID segment before MSH segment')
				return False
			pid_seen = True

		if seg_type in [u'MSH', u'PID']:
			_log.info('segment already handled')
			previous_segment = seg_type
			obr = {}
			current_result = None
			continue

		if seg_type in [u'ORC']:
			_log.info('currently ignoring %s segments', seg_type)
			previous_segment = seg_type
			obr = {}
			current_result = None
			continue

		if seg_type == u'OBR':
			previous_segment = seg_type
			last_obr = seg
			current_result = None
			obr['abbrev'] = (u'%s' % seg[OBR_field__service_name][0]).strip()
			try:
				obr['name'] = (u'%s' % seg[OBR_field__service_name][1]).strip()
			except IndexError:
				obr['name'] = obr['abbrev']
			for field_name in [OBR_field__ts_ended, OBR_field__ts_started, OBR_field__ts_specimen_received, OBR_field__ts_requested]:
				obr['clin_when'] = seg[field_name][0].strip()
				if obr['clin_when'] != u'':
					break
			continue

		if seg_type == u'OBX':
			current_result = None
			# determine value
			val_alpha = seg[OBX_field__value][0].strip()
			is_num, val_num = gmTools.input2decimal(initial = val_alpha)
			if is_num:
				val_alpha = None
			else:
				val_num = None
				val_alpha = val_alpha.replace('\.br\\', u'\n')
			# determine test type
			unit = seg[OBX_field__unit][0].strip()
			if unit == u'':
				if is_num:
					unit = u'1/1'
				else:
					unit = None
			test_type = __find_or_create_test_type (
				loinc = u'%s' % seg[OBX_field__type][0][OBX_component__loinc-1],
				name = u'%s' % seg[OBX_field__type][0][OBX_component__name-1],
				pk_lab = gm_lab['pk_test_org'],
				unit = unit
			)
			# eventually, episode should be read from lab_request
			epi = emr.add_episode (
				link_obj = conn,
				episode_name = u'administrative',
				is_open = False,
				allow_dupes = False
			)
			current_result = emr.add_test_result (
				link_obj = conn,
				episode = epi['pk_episode'],
				type = test_type['pk_test_type'],
				intended_reviewer = gmStaff.gmCurrentProvider()['pk_staff'],
				val_num = val_num,
				val_alpha = val_alpha,
				unit = unit
			)
			# handle range information et al
			ref_range = seg[OBX_field__range][0].strip()
			if ref_range != u'':
				current_result.reference_range = ref_range
			flag = seg[OBX_field__abnormal_flag][0].strip()
			if flag != u'':
				current_result['abnormality_indicator'] = flag
			current_result['status'] = seg[OBX_field__status][0].strip()
			current_result['val_grouping'] = seg[OBX_field__subid][0].strip()
			current_result['source_data'] = u''
			if last_obr is not None:
				current_result['source_data'] += unicode(last_obr)
				current_result['source_data'] += u'\n'
			current_result['source_data'] += unicode(seg)
			clin_when = seg[OBX_field__timestamp][0].strip()
			if clin_when == u'':
				_log.warning('no <Observation timestamp> in OBX, trying OBR timestamp')
				clin_when = obr['clin_when']
			try:
				clin_when = __hl7dt2pydt(clin_when)
			except ValueError:
				_log.exception('clin_when from OBX or OBR not useable, assuming <today>')
			if clin_when is not None:
				current_result['clin_when'] = clin_when
			current_result.save(conn = conn)
			when_list[gmDateTime.pydt_strftime(current_result['clin_when'], '%Y %b %d')] = 1
			previous_segment = seg_type
			continue

		if seg_type == u'NTE':
			note = seg[NET_field__note][0].strip().replace('\.br\\', u'\n')
			if note == u'':
				_log.debug('empty NTE segment')
				previous_segment = seg_type			# maybe not ? (HL7 providers happen to use empty NTE segments to "structure" raw HL7 |-)
				continue

			# if this is an NTE following an OBR (IOW an order-related
			# comment): make this a test result all of its own :-)
			if previous_segment == u'OBR':
				_log.debug('NTE following OBR: general note, using OBR timestamp [%s]', obr['clin_when'])
				current_result = None
				name = obr['name']
				if name == u'':
					name = _('Comment')
				# FIXME: please suggest a LOINC for "order comment"
				test_type = __find_or_create_test_type(name = name, pk_lab = gm_lab['pk_test_org'], abbrev = obr['abbrev'])
				# eventually, episode should be read from lab_request
				epi = emr.add_episode (
					link_obj = conn,
					episode_name = u'administrative',
					is_open = False,
					allow_dupes = False
				)
				nte_result = emr.add_test_result (
					link_obj = conn,
					episode = epi['pk_episode'],
					type = test_type['pk_test_type'],
					intended_reviewer = gmStaff.gmCurrentProvider()['pk_staff'],
					val_alpha = note
				)
				#nte_result['val_grouping'] = seg[OBX_field__subid][0].strip()
				nte_result['source_data'] = unicode(seg)
				try:
					nte_result['clin_when'] = __hl7dt2pydt(obr['clin_when'])
				except ValueError:
					_log.exception('no .clin_when from OBR for NTE pseudo-OBX available')
				nte_result.save(conn = conn)
				continue

			if (previous_segment == u'OBX') and (current_result is not None):
				current_result['source_data'] += u'\n'
				current_result['source_data'] += unicode(seg)
				current_result['note_test_org'] = gmTools.coalesce (
					current_result['note_test_org'],
					note,
					u'%%s\n%s' % note
				)
				current_result.save(conn = conn)
				previous_segment = seg_type
				continue

			_log.error(u'unexpected NTE segment')
			had_errors = True
			break

		_log.error('unknown segment, aborting')
		_log.debug('line: %s', seg)
		had_errors = True
		break

	if had_errors:
		conn.rollback()
		return False

	conn.commit()

	# record import in chart
	try:
		no_results = len(HL7.segments('OBX'))
	except KeyError:
		no_results = u'?'
	soap = _(
		'Imported HL7 file [%s]:\n'
		' lab "%s" (%s@%s), %s results (%s)'
	) % (
		filename,
		hl7_lab,
		gm_lab['unit'],
		gm_lab['organization'],
		no_results,
		u' / '.join(when_list.keys())
	)
	epi = emr.add_episode (
		episode_name = u'administrative',
		is_open = False,
		allow_dupes = False
	)
	emr.add_clin_narrative (
		note = soap,
		soap_cat = None,
		episode = epi
	)

	# keep copy of HL7 data in document archive
	folder = gmPerson.cPatient(emr.pk_patient).document_folder
	hl7_docs = folder.get_documents (
		doc_type = u'HL7 data',
		episodes = [epi['pk_episode']],
		order_by = u'ORDER BY clin_when DESC'
	)
	if len(hl7_docs) > 0:
		# there should only ever be one unless the user manually creates more,
		# also, it should always be the latest since "ORDER BY clin_when DESC"
		hl7_doc = hl7_docs[0]
	else:
		hl7_doc = folder.add_document (
			document_type = u'HL7 data',
			encounter = emr.active_encounter['pk_encounter'],
			episode = epi['pk_episode']
		)
		hl7_doc['comment'] = _('list of imported HL7 data files')
	hl7_doc['clin_when'] = gmDateTime.pydt_now_here()
	hl7_doc.save()
	part = hl7_doc.add_part(file = filename)
	part['obj_comment'] = _('Result dates: %s') % u' / '.join(when_list.keys())
	part.save()
	hl7_doc.set_reviewed(technically_abnormal = False, clinically_relevant = False)

	return True

#------------------------------------------------------------
# this is only used for testing here in this file
def __stage_MSH_as_incoming_data(filename, source=None, logfile=None):
	"""Consumes single-MSH single-PID HL7 files."""

	_log.debug('staging [%s] as unmatched incoming HL7%s', gmTools.coalesce(source, u'', u' (%s)'), filename)

	# parse HL7
	MSH_file = io.open(filename, mode = 'rt', encoding = 'utf8')
	raw_hl7 = MSH_file.read(1024 * 1024 * 5)	# 5 MB max
	MSH_file.close()
	formatted_hl7 = format_hl7_message (
		message = raw_hl7,
		skip_empty_fields = True,
		eol = u'\n'
	)
	HL7 = pyhl7.parse(raw_hl7)
	del raw_hl7

	# import file
	inc = create_incoming_data(u'HL7%s' % gmTools.coalesce(source, u'', u' (%s)'), filename)
	if inc is None:
		return None
	inc.update_data_from_file(fname = filename)
	inc['comment'] = formatted_hl7
	if logfile is not None:
		log = io.open(logfile, mode = 'rt', encoding = 'utf8')
		inc['comment'] += u'\n'
		inc['comment'] += (u'-' * 80)
		inc['comment'] += u'\n\n'
		inc['comment'] += log.read()
		log.close()
	try:
		inc['lastnames'] = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__lastname)
		inc['firstnames'] = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__firstname)
		val = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__middlename)
		if val is not None:
			inc['firstnames'] += u' '
			inc['firstnames'] += val
		val = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__dob)
		if val is not None:
			tmp = time.strptime(val, '%Y%m%d')
			inc['dob'] = pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)
		val = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__gender)
		if val is not None:
			inc['gender'] = val
		inc['external_data_id'] = filename
		#u'fk_patient_candidates',
		#	u'request_id',						# request ID as found in <data>
		#	u'postcode',
		#	u'other_info',						# other identifying info in .data
		#	u'requestor',						# Requestor of data (e.g. who ordered test results) if available in source data.
		#	u'fk_identity_disambiguated',
		#	u'comment',							# a free text comment on this row, eg. why is it here, error logs etc
		#	u'fk_provider_disambiguated'		# The provider the data is relevant to.
	except KeyError:
		_log.exception('no PID segment, cannot add more data')
	inc.save()

	return inc

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2

	gmDateTime.init()
	gmTools.gmPaths()

	#-------------------------------------------------------
	def test_import_HL7(filename):
		# would normally be set by external configuration:
		from Gnumed.business import gmPraxis
		gmPraxis.gmCurrentPraxisBranch(branch = gmPraxis.get_praxis_branches()[0])
		if not import_hl7_file(filename):
			print "error with", filename
	#-------------------------------------------------------
	def test_xml_extract():
		hl7 = extract_HL7_from_XML_CDATA(sys.argv[2], u'.//Message')
		print "HL7:", hl7
		#result, PID_fnames = split_hl7_file(hl7)
		#print "result:", result
		#print "per-PID MSH files:"
		#for name in PID_fnames:
		#	print " ", name
	#-------------------------------------------------------
	def test_incoming_data():
		for d in get_incoming_data():
			print d
	#-------------------------------------------------------
	def test_stage_hl7_from_xml():
		hl7 = extract_HL7_from_XML_CDATA(sys.argv[2], u'.//Message')
		print "HL7:", hl7
		result, PID_fnames = split_hl7_file(hl7)
		print "result:", result
		print "staging per-PID HL7 files:"
		for name in PID_fnames:
			print " file:", name
			__stage_MSH_as_incoming_data(name, source = u'Excelleris')
	#-------------------------------------------------------
	def test_split_hl7_file():
		result, PID_fnames = split_hl7_file(sys.argv[2])
		print "result:", result
		print "per-PID HL7 files:"
		for name in PID_fnames:
			print " file:", name
	#-------------------------------------------------------
	def test_stage_hl7():
		fixed = __fix_malformed_hl7_file(sys.argv[2])
		print "fixed HL7:", fixed
		PID_fnames = split_HL7_by_PID(fixed, encoding='utf8')
		print "staging per-PID HL7 files:"
		for name in PID_fnames:
			print " file:", name
			#print "", __stage_MSH_as_incoming_data(name, source = u'?')
	#-------------------------------------------------------
	def test_format_hl7_message():
		tests = [
			"OBR|1||03-1350023-LIP-0|LIP^Lipids||20031004073300|20031004073300|||||||20031004073300||22333^MEDIC^IAN^TEST||031350023||03-1350023|031350023|20031004131600||CHEM|F|||22333^MEDIC^IAN^TEST",
			"OBX|2|NM|22748-8^LDL Cholesterol||4.0|mmol/L|1.5 - 3.4|H|||F|||20031004073300"
		]
		for test in tests:
			print format_hl7_message (
#				skip_empty_fields = True,
				message = test
			)
	#-------------------------------------------------------
	def test_format_hl7_file(filename):
		fixed = __fix_malformed_hl7_file(filename)
		print format_hl7_file (
			fixed,
#			skip_empty_fields = True
			return_filename = True
		)
	#-------------------------------------------------------
	def test___fix_malformed_hl7():
		print "fixed HL7:", __fix_malformed_hl7_file(sys.argv[2])
	#-------------------------------------------------------
	#test_import_HL7(sys.argv[2])
	test_xml_extract()
	#test_incoming_data()
	#test_stage_hl7_from_xml()
	#test_stage_hl7()
	#test_format_hl7_message()
	#test_format_hl7_file(sys.argv[2])
	#test___fix_malformed_hl7()
	#test_split_hl7_file()
