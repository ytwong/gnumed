#!/bin/bash


# useful for reproducing problems with certain LOCALE settings
# (set values from a --debug log file)
#export LANGUAGE=
#export LC_NUMERIC=
#export LC_MESSAGES=
#export LC_MONETARY=
#export LC_COLLATE=
#export LC_CTYPE=
#export LC_ALL=
#export LC_TIME=
#export LANG=


# source systemwide startup extension shell script if it exists
if [ -r /etc/gnumed/gnumed-startup-local.sh ] ; then
	echo "running /etc/gnumed/gnumed-startup-local.sh"
	. /etc/gnumed/gnumed-startup-local.sh
fi


# source local startup extension shell script if it exists
if [ -r ${HOME}/.gnumed/scripts/gnumed-startup-local.sh ] ; then
	echo "running ${HOME}/.gnumed/scripts/gnumed-startup-local.sh"
	. ${HOME}/.gnumed/scripts/gnumed-startup-local.sh
fi


# standard options
LOG="--log-file=gm-from-vcs.log"
CONF="--conf-file=gm-from-vcs.conf"

# options useful for development and debugging:
DEV_OPTS="--override-schema-check --skip-update-check --local-import --debug"
# --profile=gm-from-vcs.prof

# options for running from released tarballs:
TARBALL_OPTS="--local-import --debug"
# --skip-update-check

#PSYCOPG_DEBUG="on"		# should actually be done within gnumed.py based on --debug


# eventually run it
# - devel version:
echo "-------------------------------------------------"
echo "Running from Git branch: "`git branch | grep \*`
echo "-------------------------------------------------"
python gnumed.py ${LOG} ${CONF} ${DEV_OPTS} $@

# - released tarball version:
#python gnumed.py ${LOG} ${CONF} ${TARBALL_OPTS} $@

# - production version:
#python gnumed.py ${LOG} ${CONF} $@

# - production version with HIPAA support:
#python gnumed.py ${LOG} ${CONF} --hipaa $@


# source systemwide shutdown extension shell script if it exists
if [ -r /etc/gnumed/gnumed-shutdown-local.sh ] ; then
	. /etc/gnumed/gnumed-shutdown-local.sh
fi


# source local shutdown extension shell script if it exists
if [ -r ${HOME}/.gnumed/scripts/gnumed-shutdown-local.sh ] ; then
	. ${HOME}/.gnumed/scripts/gnumed-shutdown-local.sh
fi
