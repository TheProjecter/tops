"""
Implements a read-write proxy for the TCC command interpreter

Defines the custom data types associated with the TCC's command
interpreter, and implements a proxy that can issue commands via a pair
of telnet sessions: one connected to the VMS DCL command line and the
other connected to a TCC interpreter session command line.

Refer to the proxy declaration below for details of its operating states
and archive records. Running this module will start the proxy and so
requires that the logging and archiving servers are already up.
"""

## @package tops.sdss3.tcc.session
# Implements a read-write proxy for the TCC command interpreter
#
# @author David Kirkby, dkirkby@uci.edu
# @date Created 13-Sep-2008
#
# This project is hosted at http://tops.googlecode.com/

#from tops.core.network.proxy import *

from tops.core.network.telnet import TelnetSession

class VMSSession(TelnetSession):

	login_prompt = 'Username: '
	password_prompt = 'Password: '
	command_prompt = '$ '

class TCCSession(VMSSession):
	pass


def got_users(response):
	users = { 'TCC':0, 'TCCUSER':0 }
	parser = re.compile('\s*(TCC|TCCUSER)\s+([0-9]+)')
	for line in response:
		match = parser.match(line)
		if match:
			users[match.group(1)] = match.group(2)
	for stats in users.iteritems():
		print '%s is running %d processes' % stats

def show_users():
	print "Running show_users..."
	TelnetSession.do('VMS','show users').addCallback(got_users)

if __name__ == "__main__":
	
	from getpass import getpass
	from twisted.internet import reactor,task
	from tops.core.network.telnet import prepareTelnetSession

	(hostname,port,username) = ('tcc25m.apo.nmsu.edu',23,'tcc')
	password = getpass('Enter password for %s@%s: ' % (username,hostname))
	
	prepareTelnetSession(VMSSession('VMS',username,password,debug=True),hostname,port)
#	prepareTelnetSession(LocalhostSession('localhost',username,password,debug=False),hostname,port)
	
	looper = task.loopingCall(show_users)
	looper.start(1.0)
	
	reactor.run()