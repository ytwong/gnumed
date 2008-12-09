"""GNUmed hooks framework.

This module provides convenience functions and definitions
for accessing the GNUmed hooks framework.

This framework calls the script

	~/.gnumed/scripts/hook_script.py

at various times during client execution. The script must
contain a function

def run_script(hook=None):
	pass

which accepts a single argument <hook>. That argument will
contain the hook that is being activated.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.
"""
# ========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmHooks.py,v $
# $Id: gmHooks.py,v 1.18 2008-12-09 23:25:43 ncq Exp $
__version__ = "$Revision: 1.18 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"


# stdlib
import os, sys, stat, logging

_log = logging.getLogger('gm.hook')
_log.info(__version__)


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmTools

# ========================================================================
known_hooks = [
	u'post_patient_activation',

	u'shutdown-post-GUI',
	u'startup-after-GUI-init',
	u'startup-before-GUI',

	u'request_user_attention',
	u'app_activated_startup',
	u'app_activated',
	u'app_deactivated',

	u'after_new_doc_created',
	u'before_print_doc',
	u'before_fax_doc',
	u'before_mail_doc',
	u'before_print_doc_part',
	u'before_fax_doc_part',
	u'before_mail_doc_part',
	u'before_external_doc_access',

	u'db_maintenance_warning'
]

_log.debug('known hooks:')
for hook in known_hooks:
	_log.debug(hook)

# ========================================================================
hook_module = None

def import_hook_module(reimport=False):

	global hook_module
	if not reimport:
		if hook_module is not None:
			return True

	# hardcoding path and script name allows us to
	# not need configuration for it, the environment
	# can always be detected at runtime (workplace etc)
	script_name = 'hook_script.py'
	script_path = os.path.expanduser(os.path.join('~', '.gnumed', 'scripts'))
	full_script = os.path.join(script_path, script_name)

	if not os.access(full_script, os.F_OK):
		_log.warning('creating default hook script')
		f = open(full_script, 'w')
		f.write("""
# known hooks:
#  %s

def run_script(hook=None):
	pass
""" % '#  '.join(known_hooks))
		f.close()
		os.chmod(full_script, 384)

	if os.path.islink(full_script):
		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Script must not be a link: [%s].') % full_script
		)
		return False

	if not os.access(full_script, os.R_OK):
		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Script must be readable by the calling user: [%s].') % full_script
		)
		return False

	script_mode = stat.S_IMODE(os.stat(full_script).st_mode)
	if script_mode != 384:				# octal 0600
		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Script must be readable by the calling user only (permissions "0600"): [%s].') % full_script
		)
		return False

	try:
		tmp = gmTools.import_module_from_directory(script_path, script_name)
	except StandardError:
		_log.exception('cannot import hook script')
		return False

	hook_module = tmp
#	if reimport:
#		reload(tmp)			# this has well-known shortcomings !

	_log.info('hook script: %s', full_script)
	return True
# ========================================================================
def run_hook_script(hook=None):
	# NOTE: this just *might* be a huge security hole

	if hook not in known_hooks:
		raise ValueError('run_hook_script(): unknown hook [%s]' % hook)

	if not import_hook_module(reimport = False):
		return False

	try:
		hook_module.run_script(hook = hook)
	except StandardError:
		_log.exception('error running hook script for [%s]', hook)
		gmDispatcher.send (
			signal = u'statustext',
			msg = _('Error running hook [%s] script.') % hook,
			beep = True
		)
		return False

	return True
# ========================================================================
if __name__ == '__main__':

	run_hook_script(hook = 'shutdown-post-GUI')
	run_hook_script(hook = 'invalid hook')

# ========================================================================
# $Log: gmHooks.py,v $
# Revision 1.18  2008-12-09 23:25:43  ncq
# - prepare hook script reload infrastructure
#
# Revision 1.17  2008/11/23 12:44:00  ncq
# - add hook after_new_doc_created
# - since a hook value of None is not in known_hooks do not run an extra check for it
#
# Revision 1.16  2008/09/09 22:03:01  ncq
# - fix typo
#
# Revision 1.15  2008/09/09 20:17:45  ncq
# - add some logging
# - don't crash on hook script errors
#
# Revision 1.14  2008/05/31 16:32:04  ncq
# - add before external doc access hook
#
# Revision 1.13  2008/05/19 15:45:39  ncq
# - slightly better wording
#
# Revision 1.12  2008/04/28 13:32:07  ncq
# - run hook on database maintenance notification - so maybe
#   user can be paged to his desk to close GNUmed clients
#
# Revision 1.11  2008/04/12 19:17:35  ncq
# - doc part hooks
#
# Revision 1.10  2008/04/11 23:11:52  ncq
# - add fax/mail/print hooks
# - list known hooks when creating hook script
#
# Revision 1.9  2008/01/27 21:10:34  ncq
# - fix stat()ing of the hook script
#
# Revision 1.8  2008/01/22 22:03:25  ncq
# - import hook script once only
#
# Revision 1.7  2007/11/03 17:54:04  ncq
# - added hooks
#
# Revision 1.6  2007/08/12 00:06:07  ncq
# - no more gmSignals.py
#
# Revision 1.5  2007/07/10 20:51:20  ncq
# - hooks_registry -> known_hooks
#
# Revision 1.4  2007/04/20 08:21:42  ncq
# - improved docs
#
# Revision 1.3  2007/04/01 15:29:22  ncq
# - create hook script on first use if not existant
# - improve test
#
# Revision 1.2  2007/03/26 14:42:27  ncq
# - register startup-after-GUI-init
#
# Revision 1.1  2007/03/18 13:19:13  ncq
# - factor out hooks framework
#
#