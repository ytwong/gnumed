# -*- coding: utf-8 -*-
"""Code handling drug data sources (such as databases).

license: GPL v2 or later
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys
import csv
import os
import io
import logging
import subprocess
import re as regex
from xml.etree import ElementTree as etree


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmShellAPI
from Gnumed.business import gmMedication
from Gnumed.business import gmCoding


_log = logging.getLogger('gm.meds')

#============================================================
# generic drug data source interface class
#------------------------------------------------------------
class cDrugDataSourceInterface(object):

	#--------------------------------------------------------
	def __init__(self):
		self.patient = None
		self.reviewer = None
		self.custom_path_to_binary = None
	#--------------------------------------------------------
	def get_data_source_version(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def create_data_source_entry(self):
		raise NotImplementedError
	#--------------------------------------------------------
	def switch_to_frontend(self, blocking=False):
		raise NotImplementedError
	#--------------------------------------------------------
	def import_drugs(self):
		self.switch_to_frontend()
	#--------------------------------------------------------
	def check_interactions(self, substance_intakes=None):
		self.switch_to_frontend()
	#--------------------------------------------------------
	def show_info_on_drug(self, substance_intake=None):
		self.switch_to_frontend()
	#--------------------------------------------------------
	def show_info_on_substance(self, substance_intake=None):
		self.switch_to_frontend()
	#--------------------------------------------------------
	def prescribe(self, substance_intakes=None):
		self.switch_to_frontend()
		return []

#============================================================
# Gelbe Liste
#------------------------------------------------------------
# wishlist:
# - --conf-file= for glwin.exe
# - wirkstoff: Konzentration auch in Multiprodukten
# - wirkstoff: ATC auch in Multiprodukten
# - Suche nach ATC per CLI

class cGelbeListeCSVFile(object):
	"""Iterator over a Gelbe Liste/MMI v8.2 CSV file."""

	version = u'Gelbe Liste/MMI v8.2 CSV file interface'
	default_transfer_file_windows = r"c:\rezept.txt"
	#default_encoding = 'cp1252'
	default_encoding = 'cp1250'
	csv_fieldnames = [
		u'name',
		u'packungsgroesse',					# obsolete, use "packungsmenge"
		u'darreichungsform',
		u'packungstyp',
		u'festbetrag',
		u'avp',
		u'hersteller',
		u'rezepttext',
		u'pzn',
		u'status_vertrieb',
		u'status_rezeptpflicht',
		u'status_fachinfo',
		u'btm',
		u'atc',
		u'anzahl_packungen',
		u'zuzahlung_pro_packung',
		u'einheit',
		u'schedule_morgens',
		u'schedule_mittags',
		u'schedule_abends',
		u'schedule_nachts',
		u'status_dauermedikament',
		u'status_hausliste',
		u'status_negativliste',
		u'ik_nummer',
		u'status_rabattvertrag',
		u'wirkstoffe',
		u'wirkstoffmenge',
		u'wirkstoffeinheit',
		u'wirkstoffmenge_bezug',
		u'wirkstoffmenge_bezugseinheit',
		u'status_import',
		u'status_lifestyle',
		u'status_ausnahmeliste',
		u'packungsmenge',
		u'apothekenpflicht',
		u'status_billigere_packung',
		u'rezepttyp',
		u'besonderes_arzneimittel',			# Abstimmungsverfahren SGB-V
		u't_rezept_pflicht',				# Thalidomid-Rezept
		u'erstattbares_medizinprodukt',
		u'hilfsmittel',
		u'hzv_rabattkennung',
		u'hzv_preis'
	]
	boolean_fields = [
		u'status_rezeptpflicht',
		u'status_fachinfo',
		u'btm',
		u'status_dauermedikament',
		u'status_hausliste',
		u'status_negativliste',
		u'status_rabattvertrag',
		u'status_import',
		u'status_lifestyle',
		u'status_ausnahmeliste',
		u'apothekenpflicht',
		u'status_billigere_packung',
		u'besonderes_arzneimittel',			# Abstimmungsverfahren SGB-V
		u't_rezept_pflicht',
		u'erstattbares_medizinprodukt',
		u'hilfsmittel'
	]
	#--------------------------------------------------------
	def __init__(self, filename=None):

		_log.info(cGelbeListeCSVFile.version)

		self.filename = filename
		if filename is None:
			self.filename = cGelbeListeCSVFile.default_transfer_file_windows

		_log.debug('reading Gelbe Liste/MMI drug data from [%s]', self.filename)

		self.csv_file = io.open(filename, mode = 'rt', encoding = cGelbeListeCSVFile.default_encoding)

		self.csv_lines = gmTools.unicode_csv_reader (
			self.csv_file,
			fieldnames = cGelbeListeCSVFile.csv_fieldnames,
			delimiter = ';',
			quotechar = '"',
			dict = True
		)
	#--------------------------------------------------------
	def __iter__(self):
		return self
	#--------------------------------------------------------
	def next(self):
		line = self.csv_lines.next()

		for field in cGelbeListeCSVFile.boolean_fields:
			line[field] = (line[field].strip() == u'T')

		# split field "Wirkstoff" by ";"
		if line['wirkstoffe'].strip() == u'':
			line['wirkstoffe'] = []
		else:
			line['wirkstoffe'] = [ wirkstoff.strip() for wirkstoff in line['wirkstoffe'].split(u';') ]

		return line
	#--------------------------------------------------------
	def close(self, truncate=True):
		try: self.csv_file.close()
		except: pass

		if truncate:
			try: os.open(self.filename, 'wb').close
			except: pass
	#--------------------------------------------------------
	def _get_has_unknown_fields(self):
		return (gmTools.default_csv_reader_rest_key in self.csv_fieldnames)

	has_unknown_fields = property(_get_has_unknown_fields, lambda x:x)

#============================================================
class cGelbeListeWindowsInterface(cDrugDataSourceInterface):
	"""Support v8.2 CSV file interface only."""

	version = u'Gelbe Liste/MMI v8.2 interface'
	default_encoding = 'cp1250'
	bdt_line_template = u'%03d6210#%s\r\n'		# Medikament verordnet auf Kassenrezept
	bdt_line_base_length = 8
	#--------------------------------------------------------
	def __init__(self):

		cDrugDataSourceInterface.__init__(self)

		_log.info(u'%s (native Windows)', cGelbeListeWindowsInterface.version)

		self.path_to_binary = r'C:\Programme\MMI PHARMINDEX\glwin.exe'
		self.args = r'-KEEPBACKGROUND -PRESCRIPTIONFILE %s -CLOSETOTRAY'

		paths = gmTools.gmPaths()

		self.default_csv_filename = os.path.join(paths.tmp_dir, 'rezept.txt')
		self.default_csv_filename_arg = paths.tmp_dir
		self.interactions_filename = os.path.join(paths.tmp_dir, 'gm2mmi.bdt')
		self.data_date_filename = r'C:\Programme\MMI PHARMINDEX\datadate.txt'

		self.__data_date = None
		self.__online_update_date = None

		# use adjusted config.dat
	#--------------------------------------------------------
	def get_data_source_version(self, force_reload=False):

		if self.__data_date is not None:
			if not force_reload:
				return {
					'data': self.__data_date,
					'online_update': self.__online_update_date
				}
		try:
			open(self.data_date_filename, 'wb').close()
		except Exception:
			_log.error('problem querying the MMI drug database for version information')
			_log.exception('cannot create MMI drug database version file [%s]', self.data_date_filename)
			self.__data_date = None
			self.__online_update_date = None
			return {
				'data': u'?',
				'online_update': u'?'
			}

		cmd = u'%s -DATADATE' % self.path_to_binary
		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = True):
			_log.error('problem querying the MMI drug database for version information')
			self.__data_date = None
			self.__online_update_date = None
			return {
				'data': u'?',
				'online_update': u'?'
			}

		try:
			version_file = io.open(self.data_date_filename, mode = 'rt', encoding = 'utf8')
		except Exception:
			_log.error('problem querying the MMI drug database for version information')
			_log.exception('cannot open MMI drug database version file [%s]', self.data_date_filename)
			self.__data_date = None
			self.__online_update_date = None
			return {
				'data': u'?',
				'online_update': u'?'
			}

		self.__data_date = version_file.readline()[:10]
		self.__online_update_date = version_file.readline()[:10]
		version_file.close()

		return {
			'data': self.__data_date,
			'online_update': self.__online_update_date
		}
	#--------------------------------------------------------
	def create_data_source_entry(self):
		versions = self.get_data_source_version()

		return gmCoding.create_data_source (
			long_name = u'Medikamentendatenbank "mmi PHARMINDEX" (Gelbe Liste)',
			short_name = u'GL/MMI',
			version = u'Daten: %s, Preise (Onlineupdate): %s' % (versions['data'], versions['online_update']),
			source = u'Medizinische Medien Informations GmbH, Am Forsthaus Gravenbruch 7, 63263 Neu-Isenburg',
			language = u'de'
		)
	#--------------------------------------------------------
	def switch_to_frontend(self, blocking=False, cmd=None):

		try:
			# must make sure csv file exists
			open(self.default_csv_filename, 'wb').close()
		except IOError:
			_log.exception('problem creating GL/MMI <-> GNUmed exchange file')
			return False

		if cmd is None:
			cmd = (u'%s %s' % (self.path_to_binary, self.args)) % self.default_csv_filename_arg

		if os.name == 'nt':
			blocking = True
		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = blocking):
			_log.error('problem switching to the MMI drug database')
			# apparently on the first call MMI does not
			# consistently return 0 on success
#			return False

		return True
	#--------------------------------------------------------
	def __let_user_select_drugs(self):

		# better to clean up interactions file
		open(self.interactions_filename, 'wb').close()

		if not self.switch_to_frontend(blocking = True):
			return None

		return cGelbeListeCSVFile(filename = self.default_csv_filename)
	#--------------------------------------------------------
	def import_drugs_as_substances(self):

		selected_drugs = self.__let_user_select_drugs()
		if selected_drugs is None:
			return None

		new_substances = []

		for drug in selected_drugs:
			atc = None							# hopefully MMI eventually supports atc-per-substance in a drug...
			if len(drug['wirkstoffe']) == 1:
				atc = drug['atc']
			for wirkstoff in drug['wirkstoffe']:
				new_substances.append(gmMedication.create_substance_dose(substance = wirkstoff, atc = atc, amount = amount, unit = unit))

		selected_drugs.close()

		return new_substances
	#--------------------------------------------------------
	def import_drugs(self):

		selected_drugs = self.__let_user_select_drugs()
		if selected_drugs is None:
			return None

		data_src_pk = self.create_data_source_entry()

		new_drugs = []
		new_substances = []

		for entry in selected_drugs:

			_log.debug('importing drug: %s %s', entry['name'], entry['darreichungsform'])

			if entry[u'hilfsmittel']:
				_log.debug('skipping Hilfsmittel')
				continue

			if entry[u'erstattbares_medizinprodukt']:
				_log.debug('skipping sonstiges Medizinprodukt')
				continue

			# create drug product (or get it if it already exists)
			drug = gmMedication.create_drug_product(product_name = entry['name'], preparation = entry['darreichungsform'])
			if drug is None:
				drug = gmMedication.get_drug_by_name(product_name = entry['name'], preparation = entry['darreichungsform'])
			new_drugs.append(drug)

			# update fields
			drug['is_fake_product'] = False
			drug['atc'] = entry['atc']
			drug['external_code_type'] = u'DE-PZN'
			drug['external_code'] = entry['pzn']
			drug['fk_data_source'] = data_src_pk
			drug.save()

			# add components to drug
			atc = None							# hopefully MMI eventually supports atc-per-substance in a drug...
			if len(entry['wirkstoffe']) == 1:
				atc = entry['atc']
			for wirkstoff in entry['wirkstoffe']:
				drug.add_component(substance = wirkstoff, atc = atc)

			# create as substance doses, too
			atc = None							# hopefully MMI eventually supports atc-per-substance in a drug...
			if len(entry['wirkstoffe']) == 1:
				atc = entry['atc']
			for wirkstoff in entry['wirkstoffe']:
				new_substances.append(gmMedication.create_substance_dose(substance = wirkstoff, atc = atc, amount = amount, unit = unit))

		return new_drugs, new_substances
	#--------------------------------------------------------
	def check_interactions(self, drug_ids_list=None, substances=None):
		"""For this to work the BDT interaction check must be configured in the MMI."""

		if drug_ids_list is None:
			if substances is None:
				return
			if len(substances) < 2:
				return
			drug_ids_list = [ (s.external_code_type, s.external_code) for s in substances ]
			drug_ids_list = [ code_value for code_type, code_value in drug_ids_list if (code_value is not None) and (code_type == u'DE-PZN')]

		else:
			if len(drug_ids_list) < 2:
				return

		if drug_ids_list < 2:
			return

		bdt_file = io.open(self.interactions_filename, mode = 'wt', encoding = cGelbeListeWindowsInterface.default_encoding)

		for pzn in drug_ids_list:
			pzn = pzn.strip()
			lng = cGelbeListeWindowsInterface.bdt_line_base_length + len(pzn)
			bdt_file.write(cGelbeListeWindowsInterface.bdt_line_template % (lng, pzn))

		bdt_file.close()

		self.switch_to_frontend(blocking = True)
	#--------------------------------------------------------
	def show_info_on_drug(self, drug=None):
		self.switch_to_frontend(blocking = True)
	#--------------------------------------------------------
	def show_info_on_substance(self, substance=None):

		cmd = None

		if substance.external_code_type == u'DE-PZN':
			cmd = u'%s -PZN %s' % (self.path_to_binary, substance.external_code)

		if cmd is None:
			name = gmTools.coalesce (
				substance['product'],
				substance['substance']
			)
			cmd = u'%s -NAME %s' % (self.path_to_binary, name)

		# better to clean up interactions file
		open(self.interactions_filename, 'wb').close()

		self.switch_to_frontend(cmd = cmd)

#============================================================
class cGelbeListeWineInterface(cGelbeListeWindowsInterface):

	def __init__(self):
		cGelbeListeWindowsInterface.__init__(self)

		_log.info(u'%s (WINE extension)', cGelbeListeWindowsInterface.version)

		# FIXME: if -CLOSETOTRAY is used GNUmed cannot detect the end of MMI
		self.path_to_binary = r'wine "C:\Programme\MMI PHARMINDEX\glwin.exe"'
		self.args = r'"-PRESCRIPTIONFILE %s -KEEPBACKGROUND"'

		paths = gmTools.gmPaths()

		self.default_csv_filename = os.path.join(paths.home_dir, '.wine', 'drive_c', 'windows', 'temp', 'mmi2gm.csv')
		self.default_csv_filename_arg = r'c:\windows\temp\mmi2gm.csv'
		self.interactions_filename = os.path.join(paths.home_dir, '.wine', 'drive_c', 'windows', 'temp', 'gm2mmi.bdt')
		self.data_date_filename = os.path.join(paths.home_dir, '.wine', 'drive_c', 'Programme', 'MMI PHARMINDEX', 'datadate.txt')

#============================================================
# FreeDiams
#------------------------------------------------------------
class cFreeDiamsInterface(cDrugDataSourceInterface):

	version = u'FreeDiams interface'
	default_encoding = 'utf8'
	default_dob_format = '%Y/%m/%d'

	map_gender2mf = {
		'm': u'M',
		'f': u'F',
		'tf': u'H',
		'tm': u'H',
		'h': u'H'
	}
	#--------------------------------------------------------
	def __init__(self):
		cDrugDataSourceInterface.__init__(self)
		_log.info(cFreeDiamsInterface.version)

		self.__imported_drugs = []

		self.__gm2fd_filename = gmTools.get_unique_filename(prefix = r'gm2freediams-', suffix = r'.xml')
		_log.debug('GNUmed -> FreeDiams "exchange-in" file: %s', self.__gm2fd_filename)
		self.__fd2gm_filename = gmTools.get_unique_filename(prefix = r'freediams2gm-', suffix = r'.xml')
		_log.debug('GNUmed <-> FreeDiams "exchange-out"/"prescription" file: %s', self.__fd2gm_filename)
		paths = gmTools.gmPaths()
		# this file can be modified by the user as needed:
		self.__fd4gm_config_file = os.path.join(paths.home_dir, '.gnumed', 'freediams4gm.conf')
		_log.debug('FreeDiams config file for GNUmed use: %s', self.__fd4gm_config_file)

		self.path_to_binary = None
		self.__detect_binary()
	#--------------------------------------------------------
	def get_data_source_version(self):
		# ~/.freediams/config.ini: [License] -> AcceptedVersion=....

		if not self.__detect_binary():
			return False

		freediams = subprocess.Popen (
			args = u'--version',				# --version or -version or -v
			executable = self.path_to_binary,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
#			close_fds = True,					# Windows can't do that in conjunction with stdout/stderr = ... :-(
			universal_newlines = True
		)
		data, errors = freediams.communicate()
		version = regex.search('FreeDiams\s\d.\d.\d', data).group().split()[1]
		_log.debug('FreeDiams %s', version)

		return version
	#--------------------------------------------------------
	def create_data_source_entry(self):
		return gmCoding.create_data_source (
			long_name = u'"FreeDiams" Drug Database Frontend',
			short_name = u'FreeDiams',
			version = self.get_data_source_version(),
			source = u'http://ericmaeker.fr/FreeMedForms/di-manual/index.html',
			language = u'fr'			# actually to be multi-locale
		)
	#--------------------------------------------------------
	def switch_to_frontend(self, blocking=False, mode='interactions'):
		"""http://ericmaeker.fr/FreeMedForms/di-manual/en/html/ligne_commandes.html"""

		_log.debug('calling FreeDiams in [%s] mode', mode)

		self.__imported_drugs = []

		if not self.__detect_binary():
			return False

		self.__create_gm2fd_file(mode = mode)

		args = u'--exchange-in="%s"' % (self.__gm2fd_filename)
		cmd = r'%s %s' % (self.path_to_binary, args)
		if os.name == 'nt':
			blocking = True
		if not gmShellAPI.run_command_in_shell(command = cmd, blocking = blocking):
			_log.error('problem switching to the FreeDiams drug database')
			return False

		if blocking == True:
			self.import_fd2gm_file_as_drugs()

		return True
	#--------------------------------------------------------
	def import_drugs(self):
		self.switch_to_frontend(blocking = True)
	#--------------------------------------------------------
	def check_interactions(self, substance_intakes=None):
		if substance_intakes is None:
			return
		if len(substance_intakes) < 2:
			return

		self.__create_prescription_file(substance_intakes = substance_intakes)
		self.switch_to_frontend(mode = 'interactions', blocking = False)
	#--------------------------------------------------------
	def show_info_on_drug(self, substance_intake=None):
		if substance_intake is None:
			return

		self.__create_prescription_file(substance_intakes = [substance_intake])
		self.switch_to_frontend(mode = 'interactions', blocking = False)
	#--------------------------------------------------------
	def show_info_on_substance(self, substance_intake=None):
		self.show_info_on_drug(substance_intake = substance_intake)
	#--------------------------------------------------------
	def prescribe(self, substance_intakes=None):
		if substance_intakes is None:
			if not self.__export_latest_prescription():
				self.__create_prescription_file()
		else:
			self.__create_prescription_file(substance_intakes = substance_intakes)

		self.switch_to_frontend(mode = 'prescription', blocking = True)
		self.import_fd2gm_file_as_prescription()

		return self.__imported_drugs
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __detect_binary(self):

		if self.path_to_binary is not None:
			return True

		found, cmd = gmShellAPI.find_first_binary(binaries = [
			r'/usr/bin/freediams',
			r'freediams',
			r'/Applications/FreeDiams.app/Contents/MacOs/FreeDiams',
			r'C:\Program Files (x86)\FreeDiams\freediams.exe',
			r'C:\Program Files\FreeDiams\freediams.exe',
			r'c:\programs\freediams\freediams.exe',
			r'freediams.exe'
		])

		if found:
			self.path_to_binary = cmd
			return True

		try:
			self.custom_path_to_binary
		except AttributeError:
			_log.error('cannot find FreeDiams binary, no custom path set')
			return False

		if self.custom_path_to_binary is None:
			_log.error('cannot find FreeDiams binary')
			return False

		found, cmd = gmShellAPI.detect_external_binary(binary = self.custom_path_to_binary)
		if found:
			self.path_to_binary = cmd
			return True

		_log.error('cannot find FreeDiams binary')
		return False
	#--------------------------------------------------------
	def __export_latest_prescription(self):

		if self.patient is None:
			_log.debug('cannot export latest FreeDiams prescriptions w/o patient')
			return False

		docs = self.patient.get_document_folder()
		prescription = docs.get_latest_freediams_prescription()
		if prescription is None:
			_log.debug('no FreeDiams prescription available')
			return False

		for part in prescription.parts:
			if part['filename'] == u'freediams-prescription.xml':
				if part.export_to_file(filename = self.__fd2gm_filename) is not None:
					return True

		_log.error('cannot export latest FreeDiams prescription to XML file')

		return False
	#--------------------------------------------------------
	def __create_prescription_file(self, substance_intakes=None):
		"""FreeDiams calls this exchange-out or prescription file.

			CIS stands for Unique Speciality Identifier (eg bisoprolol 5 mg, gel).
			CIS is AFSSAPS specific, but pharmacist can retreive drug name with the CIS.
			AFSSAPS is the French FDA.

			CIP stands for Unique Presentation Identifier (eg 30 pills plaq)
			CIP if you want to specify the packaging of the drug (30 pills
			thermoformed tablet...) -- actually not really usefull for french
			doctors.
			# .external_code_type: u'FR-CIS'
			# .external_cod: the CIS value

		OnlyForTest:
			OnlyForTest drugs will be processed by the IA Engine but
			not printed (regardless of FreeDiams mode). They are shown
			in gray in the prescription view.

			Select-only is a mode where FreeDiams creates a list of drugs
			not a full prescription. In this list, users can add ForTestOnly
			drug if they want to
				1. print the list without some drugs
				2. but including these drugs in the IA engine calculation

			Select-Only mode does not have any relation with the ForTestOnly drugs.

		IsTextual:
			What is the use and significance of the
				<IsTextual>true/false</IsTextual>
			flag when both <DrugName> and <TextualDrugName> exist ?

			This tag must be setted even if it sounds like a duplicated
			data. This tag is needed inside FreeDiams code.

		INN:
			GNUmed will pass the substance in <TextualDrugName
			and will also pass <INN>True</INN>.

			Eric:	Nop, this is not usefull because pure textual drugs
					are not processed but just shown.
		"""
		# virginize file
		open(self.__fd2gm_filename, 'wb').close()

		# make sure we've got something to do
		if substance_intakes is None:
			if self.patient is None:
				_log.warning('cannot create prescription file because there is neither a patient nor a substance intake list')
				# do fail because __export_latest_prescription() should not have been called without patient
				return False
			emr = self.patient.emr
			substance_intakes = emr.get_current_medications (
				include_inactive = False,
				include_unapproved = True
			)

		drug_snippets = []

		# process FD drugs
		fd_intakes = [ i for i in substance_intakes if (
			(i['intake_is_approved_of'] is True)
				and
			(i['external_code_type_product'] is not None)
				and
			(i['external_code_type_product'].startswith(u'FreeDiams::'))
		)]

		intakes_pooled_by_product = {}
		for intake in fd_intakes:
			# this will leave only one entry per drug
			# but FreeDiams knows the components ...
			intakes_pooled_by_product[intake['product']] = intake
		del fd_intakes

		drug_snippet = u"""<Prescription>
			<Drug u1="%s" u2="" old="%s" u3="" db="%s">		<!-- "old" needs to be the same as "u1" if not known -->
				<DrugName>%s</DrugName>						<!-- just for identification when reading XML files -->
			</Drug>
		</Prescription>"""

		last_db_id = u'CA_HCDPD'
		for intake in intakes_pooled_by_product.values():
			last_db_id = gmTools.xml_escape_string(text = intake['external_code_type_product'].replace(u'FreeDiams::', u'').split(u'::')[0])
			drug_snippets.append(drug_snippet % (
				gmTools.xml_escape_string(text = intake['external_code_product'].strip()),
				gmTools.xml_escape_string(text = intake['external_code_product'].strip()),
				last_db_id,
				gmTools.xml_escape_string(text = intake['product'].strip())
			))

		# process non-FD drugs
		non_fd_intakes = [ i for i in substance_intakes if (
			(i['intake_is_approved_of'] is True)
			and (
				(i['external_code_type_product'] is None)
					or
				(not i['external_code_type_product'].startswith(u'FreeDiams::'))
			)
		)]

		non_fd_product_intakes = [ i for i in non_fd_intakes if i['product'] is not None ]
		non_fd_substance_intakes = [ i for i in non_fd_intakes if i['product'] is None ]
		del non_fd_intakes

		drug_snippet = u"""<Prescription>
			<Drug u1="-1" u2="" old="" u3="" db="">
				<DrugName>%s</DrugName>
			</Drug>
			<Dose Note="%s" IsTextual="true" IsAld="false"/>
		</Prescription>"""
#				<DrugUidName></DrugUidName>
#				<DrugForm></DrugForm>
#				<DrugRoute></DrugRoute>
#				<DrugStrength/>

		for intake in non_fd_substance_intakes:
			drug_name = u'%s %s%s (%s)' % (
				intake['substance'],
				intake['amount'],
				intake['unit'],
				intake['l10n_preparation']
			)
			drug_snippets.append(drug_snippet % (
				gmTools.xml_escape_string(text = drug_name.strip()),
				gmTools.xml_escape_string(text = gmTools.coalesce(intake['schedule'], u''))
			))

		intakes_pooled_by_product = {}
		for intake in non_fd_product_intakes:
			prod = u'%s %s' % (intake['product'], intake['l10n_preparation'])
			try:
				intakes_pooled_by_product[prod].append(intake)
			except KeyError:
				intakes_pooled_by_product[prod] = [intake]

		for product, comps in intakes_pooled_by_product.iteritems():
			drug_name = u'%s\n' % product
			for comp in comps:
				drug_name += u'  %s %s%s\n' % (
					comp['substance'],
					comp['amount'],
					comp['unit']
			)
			drug_snippets.append(drug_snippet % (
				gmTools.xml_escape_string(text = drug_name.strip()),
				gmTools.xml_escape_string(text = gmTools.coalesce(comps[0]['schedule'], u''))
			))

		# assemble XML file
		xml = u"""<?xml version = "1.0" encoding = "UTF-8"?>
<!DOCTYPE FreeMedForms>
<FreeDiams>
	<FullPrescription version="0.7.2">
		%s
	</FullPrescription>
</FreeDiams>
"""

		xml_file = io.open(self.__fd2gm_filename, mode = 'wt', encoding = 'utf8')
		xml_file.write(xml % u'\n\t\t'.join(drug_snippets))
		xml_file.close()

		return True
	#--------------------------------------------------------
	def __create_gm2fd_file(self, mode='interactions'):

		if mode == 'interactions':
			mode = u'select-only'
		elif mode == 'prescription':
			mode = u'prescriber'
		else:
			mode = u'select-only'

		xml_file = io.open(self.__gm2fd_filename, mode = 'wt', encoding = 'utf8')

		xml = u"""<?xml version="1.0" encoding="UTF-8"?>

<FreeDiams_In version="0.5.0">
	<EMR name="GNUmed" uid="unused"/>
	<ConfigFile value="%s"/>
	<ExchangeOut value="%s" format="xml"/>
	<!-- <DrugsDatabase uid="can be set to a specific DB"/> -->
	<Ui editmode="%s" blockPatientDatas="1"/>
	%%s
</FreeDiams_In>
"""		% (
			self.__fd4gm_config_file,
			self.__fd2gm_filename,
			mode
		)

		if self.patient is None:
			xml_file.write(xml % u'')
			xml_file.close()
			return

		name = self.patient.get_active_name()
		if self.patient['dob'] is None:
			dob = u''
		else:
			dob = self.patient['dob'].strftime(cFreeDiamsInterface.default_dob_format)

		emr = self.patient.emr
		allgs = emr.get_allergies()
		atc_allgs = [
			a['atc_code'] for a in allgs if ((a['atc_code'] is not None) and (a['type'] == u'allergy'))
		]
		atc_sens = [
			a['atc_code'] for a in allgs if ((a['atc_code'] is not None) and (a['type'] == u'sensitivity'))
		]
		inn_allgs = [
			a['allergene'] for a in allgs if ((a['allergene'] is not None) and (a['type'] == u'allergy'))
		]
		inn_sens = [
			a['allergene'] for a in allgs if ((a['allergene'] is not None) and (a['type'] == u'sensitivity'))
		]
		# this is rather fragile: FreeDiams won't know what type of UID this is
		# (but it will assume it is of the type of the drug database in use)
		# but eventually FreeDiams puts all drugs into one database :-)
		uid_allgs = [
			a['substance_code'] for a in allgs if ((a['substance_code'] is not None) and (a['type'] == u'allergy'))
		]
		uid_sens = [
			a['substance_code'] for a in allgs if ((a['substance_code'] is not None) and (a['type'] == u'sensitivity'))
		]

		patient_xml = u"""<Patient>
		<Identity
			  lastnames="%s"
			  firstnames="%s"
			  uid="%s"
			  dob="%s"
			  gender="%s"
		/>
		<!-- can be <7 characters class codes: -->
		<ATCAllergies value="%s"/>
		<ATCIntolerances value="%s"/>

		<InnAllergies value="%s"/>
		<InnIntolerances value="%s"/>

		<DrugsUidAllergies value="%s"/>
		<DrugsUidIntolerances value="%s"/>

		<!--
			# FIXME: search by LOINC code and add (as soon as supported by FreeDiams ...)
			<Creatinine value="12" unit="mg/l or mmol/l"/>
			<Weight value="70" unit="kg or pd" />
			<WeightInGrams value="70"/>
			<Height value="170" unit="cm or "/>
			<HeightInCentimeters value="170"/>
			<ICD10 value="J11.0;A22;Z23"/>
		-->

	</Patient>
"""		% (
			gmTools.xml_escape_string(text = name['lastnames']),
			gmTools.xml_escape_string(text = name['firstnames']),
			self.patient.ID,
			dob,
			cFreeDiamsInterface.map_gender2mf[self.patient['gender']],
			gmTools.xml_escape_string(text = u';'.join(atc_allgs)),
			gmTools.xml_escape_string(text = u';'.join(atc_sens)),
			gmTools.xml_escape_string(text = u';'.join(inn_allgs)),
			gmTools.xml_escape_string(text = u';'.join(inn_sens)),
			gmTools.xml_escape_string(text = u';'.join(uid_allgs)),
			gmTools.xml_escape_string(text = u';'.join(uid_sens))
		)

		xml_file.write(xml % patient_xml)
		xml_file.close()
	#--------------------------------------------------------
	def import_fd2gm_file_as_prescription(self, filename=None):

		if filename is None:
			filename = self.__fd2gm_filename

		_log.debug('importing FreeDiams prescription information from [%s]', filename)

		fd2gm_xml = etree.ElementTree()
		fd2gm_xml.parse(filename)

		pdfs = fd2gm_xml.findall('ExtraDatas/Printed')
		if len(pdfs) == 0:
			_log.debug('no PDF prescription files listed')
			return

		fd_filenames = []
		for pdf in pdfs:
			fd_filenames.append(pdf.attrib['file'])

		_log.debug('listed PDF prescription files: %s', fd_filenames)

		docs = self.patient.get_document_folder()
		emr = self.patient.emr

		prescription = docs.add_prescription (
			encounter = emr.active_encounter['pk_encounter'],
			episode = emr.add_episode (
				episode_name = DEFAULT_MEDICATION_HISTORY_EPISODE,
				is_open = False
			)['pk_episode']
		)
		prescription['ext_ref'] = u'FreeDiams'
		prescription.save()
		fd_filenames.append(filename)
		success, msg, parts = prescription.add_parts_from_files(files = fd_filenames)
		if not success:
			_log.error(msg)
			return

		for part in parts:
			part['obj_comment'] = _('copy of printed prescription')
			part.save()

		xml_part = parts[-1]
		xml_part['filename'] = u'freediams-prescription.xml'
		xml_part['obj_comment'] = _('prescription data')
		xml_part.save()

		# are we the intended reviewer ?
		from Gnumed.business.gmStaff import gmCurrentProvider
		me = gmCurrentProvider()
		# if so: auto-sign the prescription
		if xml_part['pk_intended_reviewer'] == me['pk_staff']:
			prescription.set_reviewed(technically_abnormal = False, clinically_relevant = False)
	#--------------------------------------------------------
	def import_fd2gm_file_as_drugs(self, filename=None):
		"""
			If returning textual prescriptions (say, drugs which FreeDiams
			did not know) then "IsTextual" will be True and UID will be -1.
		"""
		if filename is None:
			filename = self.__fd2gm_filename

		# FIXME: do not import IsTextual drugs, or rather, make that configurable

		fd2gm_xml = etree.ElementTree()
		fd2gm_xml.parse(filename)

		data_src_pk = self.create_data_source_entry()

		xml_version = fd2gm_xml.find('FullPrescription').attrib['version']
		_log.debug('fd2gm file version: %s', xml_version)

		if xml_version in ['0.6.0', '0.7.2']:
			return self.__import_fd2gm_file_as_drugs_0_6_0(fd2gm_xml = fd2gm_xml, pk_data_source = data_src_pk)

		return self.__import_fd2gm_file_as_drugs_0_5(fd2gm_xml = fd2gm_xml, pk_data_source = data_src_pk)
	#--------------------------------------------------------
	def __import_fd2gm_file_as_drugs_0_6_0(self, fd2gm_xml=None, pk_data_source=None):

#		drug_id_name = db_def.attrib['drugUidName']
		fd_xml_prescriptions = fd2gm_xml.findall('FullPrescription/Prescription')

		self.__imported_drugs = []
		for fd_xml_prescription in fd_xml_prescriptions:
			drug_uid = fd_xml_prescription.find('Drug').attrib['u1'].strip()
			if drug_uid == u'-1':
				_log.debug('skipping textual drug')
				continue
			drug_db =  fd_xml_prescription.find('Drug').attrib['db'].strip()
			drug_uid_name = fd_xml_prescription.find('Drug/DrugUidName').text.strip()
			#drug_uid_name = u'<%s>' % drug_db
			drug_name = fd_xml_prescription.find('Drug/DrugName').text.replace(', )', ')').strip()
			drug_form = fd_xml_prescription.find('Drug/DrugForm').text.strip()
#			drug_atc = fd_xml_prescription.find('DrugATC')
#			if drug_atc is None:
#				drug_atc = u''
#			else:
#				if drug_atc.text is None:
#					drug_atc = u''
#				else:
#					drug_atc = drug_atc.text.strip()

			# create new drug product
			new_drug = gmMedication.create_drug_product(product_name = drug_name, preparation = drug_form, return_existing = True)
			self.__imported_drugs.append(new_drug)
			new_drug['is_fake_product'] = False
#			new_drug['atc'] = drug_atc
			new_drug['external_code_type'] = u'FreeDiams::%s::%s' % (drug_db, drug_uid_name)
			new_drug['external_code'] = drug_uid
			new_drug['pk_data_source'] = pk_data_source
			new_drug.save()

			# parse XML for composition records
			fd_xml_components = fd_xml_prescription.getiterator('Composition')
			comp_data = {}
			for fd_xml_comp in fd_xml_components:

				data = {}

				xml_strength = fd_xml_comp.attrib['strength'].strip()
				amount = regex.match(r'^\d+[.,]{0,1}\d*', xml_strength)
				if amount is None:
					amount = 99999
				else:
					amount = amount.group()
				data['amount'] = amount

				#unit = regex.sub(r'\d+[.,]{0,1}\d*', u'', xml_strength).strip()
				unit = (xml_strength[len(amount):]).strip()
				if unit == u'':
					unit = u'*?*'
				data['unit'] = unit

				# hopefully, FreeDiams gets their act together, eventually:
				atc = regex.match(r'[A-Za-z]\d\d[A-Za-z]{2}\d\d', fd_xml_comp.attrib['atc'].strip())
				if atc is None:
					data['atc'] = None
				else:
					atc = atc.group()
				data['atc'] = atc

				molecule_name = fd_xml_comp.attrib['molecularName'].strip()
				if molecule_name != u'':
					gmMedication.create_substance_dose(substance = molecule_name, atc = atc, amount = amount, unit = unit)
				data['molecule_name'] = molecule_name

				inn_name = fd_xml_comp.attrib['inn'].strip()
				if inn_name != u'':
					gmMedication.create_substance_dose(substance = inn_name, atc = atc, amount = amount, unit = unit)
				#data['inn_name'] = molecule_name
				data['inn_name'] = inn_name

				if molecule_name == u'':
					data['substance'] = inn_name
					_log.info('linking INN [%s] rather than molecularName as component', inn_name)
				else:
					data['substance'] = molecule_name

				data['nature'] = fd_xml_comp.attrib['nature'].strip()
				data['nature_ID'] = fd_xml_comp.attrib['natureLink'].strip()

				# merge composition records of SA/FT nature
				try:
					old_data = comp_data[data['nature_ID']]
					# normalize INN
					if old_data['inn_name'] == u'':
						old_data['inn_name'] = data['inn_name']
					if data['inn_name'] == u'':
						data['inn_name'] = old_data['inn_name']
					# normalize molecule
					if old_data['molecule_name'] == u'':
						old_data['molecule_name'] = data['molecule_name']
					if data['molecule_name'] == u'':
						data['molecule_name'] = old_data['molecule_name']
					# normalize ATC
					if old_data['atc'] == u'':
						old_data['atc'] = data['atc']
					if data['atc'] == u'':
						data['atc'] = old_data['atc']
					# FT: transformed form
					# SA: active substance
					# it would be preferable to use the SA record because that's what's *actually*
					# contained in the drug, however FreeDiams does not list the amount thereof
					# (rather that of the INN)
					# FT and SA records of the same component carry the same nature_ID
					if data['nature'] == u'FT':
						comp_data[data['nature_ID']] = data
					else:
						comp_data[data['nature_ID']] = old_data

				# or create new record
				except KeyError:
					comp_data[data['nature_ID']] = data

			# actually create components from (possibly merged) composition records
			for key, data in comp_data.items():
				new_drug.add_component (
					substance = data['substance'],
					atc = data['atc'],
					amount = data['amount'],
					unit = data['unit']
				)
	#--------------------------------------------------------
	def __import_fd2gm_file_as_drugs_0_5(self, fd2gm_xml=None, pk_data_source=None):

		db_def = fd2gm_xml.find('DrugsDatabaseName')
		db_id = db_def.text.strip()
		drug_id_name = db_def.attrib['drugUidName']
		fd_xml_drug_entries = fd2gm_xml.findall('FullPrescription/Prescription')

		self.__imported_drugs = []
		for fd_xml_drug in fd_xml_drug_entries:
			drug_uid = fd_xml_drug.find('Drug_UID').text.strip()
			if drug_uid == u'-1':
				_log.debug('skipping textual drug')
				continue		# it's a TextualDrug, skip it
			drug_name = fd_xml_drug.find('DrugName').text.replace(', )', ')').strip()
			drug_form = fd_xml_drug.find('DrugForm').text.strip()
			drug_atc = fd_xml_drug.find('DrugATC')
			if drug_atc is None:
				drug_atc = u''
			else:
				if drug_atc.text is None:
					drug_atc = u''
				else:
					drug_atc = drug_atc.text.strip()

			# create new drug product
			new_drug = gmMedication.create_drug_product(product_name = drug_name, preparation = drug_form, return_existing = True)
			self.__imported_drugs.append(new_drug)
			new_drug['is_fake_product'] = False
			new_drug['atc'] = drug_atc
			new_drug['external_code_type'] = u'FreeDiams::%s::%s' % (db_id, drug_id_name)
			new_drug['external_code'] = drug_uid
			new_drug['pk_data_source'] = pk_data_source
			new_drug.save()

			# parse XML for composition records
			fd_xml_components = fd_xml_drug.getiterator('Composition')
			comp_data = {}
			for fd_xml_comp in fd_xml_components:

				data = {}

				amount = regex.match(r'\d+[.,]{0,1}\d*', fd_xml_comp.attrib['strenght'].strip())			# sic, typo
				if amount is None:
					amount = 99999
				else:
					amount = amount.group()
				data['amount'] = amount

				unit = regex.sub(r'\d+[.,]{0,1}\d*', u'', fd_xml_comp.attrib['strenght'].strip()).strip()	# sic, typo
				if unit == u'':
					unit = u'*?*'
				data['unit'] = unit

				molecule_name = fd_xml_comp.attrib['molecularName'].strip()
				if molecule_name != u'':
					gmMedication.create_substance_dose(substance = molecule_name, atc = None, amount = amount, unit = unit)
				data['molecule_name'] = molecule_name

				inn_name = fd_xml_comp.attrib['inn'].strip()
				if inn_name != u'':
					gmMedication.create_substance_dose(substance = inn_name, atc = None, amount = amount, unit = unit)
				data['inn_name'] = molecule_name

				if molecule_name == u'':
					data['substance'] = inn_name
					_log.info('linking INN [%s] rather than molecularName as component', inn_name)
				else:
					data['substance'] = molecule_name

				data['nature'] = fd_xml_comp.attrib['nature'].strip()
				data['nature_ID'] = fd_xml_comp.attrib['natureLink'].strip()

				# merge composition records of SA/FT nature
				try:
					old_data = comp_data[data['nature_ID']]
					# normalize INN
					if old_data['inn_name'] == u'':
						old_data['inn_name'] = data['inn_name']
					if data['inn_name'] == u'':
						data['inn_name'] = old_data['inn_name']
					# normalize molecule
					if old_data['molecule_name'] == u'':
						old_data['molecule_name'] = data['molecule_name']
					if data['molecule_name'] == u'':
						data['molecule_name'] = old_data['molecule_name']
					# FT: transformed form
					# SA: active substance
					# it would be preferable to use the SA record because that's what's *actually*
					# contained in the drug, however FreeDiams does not list the amount thereof
					# (rather that of the INN)
					if data['nature'] == u'FT':
						comp_data[data['nature_ID']] = data
					else:
						comp_data[data['nature_ID']] = old_data

				# or create new record
				except KeyError:
					comp_data[data['nature_ID']] = data

			# actually create components from (possibly merged) composition records
			for key, data in comp_data.items():
				new_drug.add_component (
					substance = data['substance'],
					amount = data['amount'],
					unit = data['unit']
				)

#============================================================
# Ifap
#------------------------------------------------------------
class cIfapInterface(cDrugDataSourceInterface):
	"""empirical CSV interface"""

	def __init__(self):
		pass

	def print_transfer_file(self, filename=None):

		try:
			csv_file = io.open(filename, mode = 'rt', encoding = 'latin1')						# FIXME: encoding correct ?
		except:
			_log.exception('cannot access [%s]', filename)
			csv_file = None

		field_names = u'PZN Handelsname Form Abpackungsmenge Einheit Preis1 Hersteller Preis2 rezeptpflichtig Festbetrag Packungszahl Packungsgr\xf6\xdfe'.split()

		if csv_file is None:
			return False

		csv_lines = csv.DictReader (
			csv_file,
			fieldnames = field_names,
			delimiter = ';'
		)

		for line in csv_lines:
			print "--------------------------------------------------------------------"[:31]
			for key in field_names:
				tmp = ('%s                                                ' % key)[:30]
				print '%s: %s' % (tmp, line[key])

		csv_file.close()

#				narr = u'%sx %s %s %s (\u2258 %s %s) von %s (%s)' % (
#					line['Packungszahl'].strip(),
#					line['Handelsname'].strip(),
#					line['Form'].strip(),
#					line[u'Packungsgr\xf6\xdfe'].strip(),
#					line['Abpackungsmenge'].strip(),
#					line['Einheit'].strip(),
#					line['Hersteller'].strip(),
#					line['PZN'].strip()
#				)

#============================================================
drug_data_source_interfaces = {
	'Deutschland: Gelbe Liste/MMI (Windows)': cGelbeListeWindowsInterface,
	'Deutschland: Gelbe Liste/MMI (WINE)': cGelbeListeWineInterface,
	'FreeDiams (FR, US, CA, ZA)': cFreeDiamsInterface
}

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.business import gmPerson

	#--------------------------------------------------------
	def test_MMI_interface():
		mmi = cGelbeListeWineInterface()
		print mmi
		print "interface definition:", mmi.version
		print "database versions:   ", mmi.get_data_source_version()
	#--------------------------------------------------------
	def test_MMI_file():
		mmi_file = cGelbeListeCSVFile(filename = sys.argv[2])
		for drug in mmi_file:
			print "-------------"
			print '"%s" (ATC: %s / PZN: %s)' % (drug['name'], drug['atc'], drug['pzn'])
			for stoff in drug['wirkstoffe']:
				print " Wirkstoff:", stoff
			raw_input()
			if mmi_file.has_unknown_fields is not None:
				print "has extra data under [%s]" % gmTools.default_csv_reader_rest_key
			for key in mmi_file.csv_fieldnames:
				print key, '->', drug[key]
			raw_input()
		mmi_file.close()
	#--------------------------------------------------------
	def test_mmi_switch_to():
		mmi = cGelbeListeWineInterface()
		mmi.switch_to_frontend(blocking = True)
	#--------------------------------------------------------
	def test_mmi_let_user_select_drugs():
		mmi = cGelbeListeWineInterface()
		mmi_file = mmi.__let_user_select_drugs()
		for drug in mmi_file:
			print "-------------"
			print '"%s" (ATC: %s / PZN: %s)' % (drug['name'], drug['atc'], drug['pzn'])
			for stoff in drug['wirkstoffe']:
				print " Wirkstoff:", stoff
			print drug
		mmi_file.close()
	#--------------------------------------------------------
	def test_mmi_import_drugs():
		mmi = cGelbeListeWineInterface()
		mmi.import_drugs()
	#--------------------------------------------------------
	def test_mmi_interaction_check():
		mmi = cGelbeListeInterface()
		print mmi
		print "interface definition:", mmi.version
		# Metoprolol + Hct vs Citalopram
		diclofenac = '7587712'
		phenprocoumon = '4421744'
		mmi.check_interactions(drug_ids_list = [diclofenac, phenprocoumon])
	#--------------------------------------------------------
	# FreeDiams
	#--------------------------------------------------------
	def test_fd_switch_to():
		gmPerson.set_active_patient(patient = gmPerson.cPerson(aPK_obj = 12))
		fd = cFreeDiamsInterface()
		fd.patient = gmPerson.gmCurrentPatient()
#		fd.switch_to_frontend(blocking = True)
		fd.import_fd2gm_file_as_drugs(filename = sys.argv[2])
	#--------------------------------------------------------
	def test_fd_show_interactions():
		gmPerson.set_active_patient(patient = gmPerson.cPerson(aPK_obj = 12))
		fd = cFreeDiamsInterface()
		fd.patient = gmPerson.gmCurrentPatient()
		fd.check_interactions(substances = fd.patient.emr.get_current_medications(include_unapproved = True))

	#--------------------------------------------------------
	# MMI/Gelbe Liste
	#test_MMI_interface()
	#test_MMI_file()
	#test_mmi_switch_to()
	#test_mmi_let_user_select_drugs()
	#test_mmi_import_substances()
	#test_mmi_import_drugs()

	# FreeDiams
	#test_fd_switch_to()
	#test_fd_show_interactions()
