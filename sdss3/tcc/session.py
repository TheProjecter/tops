"""
Implements a read-write proxy for the TCC command interpreter

Defines the custom data types associated with the TCC's command
interpreter, and implements a proxy that can issue commands via a telnet
session.

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

def answer(response,command):
	print 'the answer to "%s" is:\n%s' % (command,'\n'.join(response))

def delayed1():
	print "Running delayed1..."
	TelnetSession.do('FTP','debug').addCallback(answer,'debug 1')
	TelnetSession.do('FTP','help set').addCallback(answer,'help set')
	TelnetSession.do('FTP','debug').addCallback(answer,'debug 2')

def delayed2():
	print "Running delayed2..."
	TelnetSession.do('LocalhostSession','pwd').addCallback(answer,'pwd')

	
class LocalhostSession(TelnetSession):

	login_prompt = 'login: '
	password_prompt = 'Password:'
	command_prompt = '~ % '

class FTPSession(LocalhostSession):

	ftp_command = 'ftp'
	ftp_prompt = 'ftp> '

	def session_started(self):
		self.state = 'STARTING_FTP'
		self.send(self.ftp_command + '\n')
		
	def session_STARTING_FTP(self,data):
		if data.endswith(self.ftp_prompt):
			self.command_prompt = self.ftp_prompt
			self.state = 'COMMAND_LINE_READY'

class VMSSession(TelnetSession):

	login_prompt = 'Username: '
	password_prompt = 'Password: '
	command_prompt = '$ '


from getpass import getpass
from twisted.internet import reactor
from tops.core.network.telnet import prepareTelnetSession

if __name__ == "__main__":
	
	(hostname,port,username) = ('localhost',23,'david')
	password = getpass('Enter password for %s@%s: ' % (username,hostname))
	prepareTelnetSession(FTPSession('FTP',username,password,debug=False),hostname,port)

#	connectionFactory = protocol.ClientFactory()
#	connectionFactory.protocol = TelnetConnection
#	reactor.connectTCP('localhost',23,connectionFactory)
	#reactor.connectTCP('tcc25m.apo.nmsu.edu',23,connectionFactory)
	
	reactor.callLater(3.0,delayed1)
	
	reactor.run()
