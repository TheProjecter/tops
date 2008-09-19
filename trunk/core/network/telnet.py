"""
Supports remote operations via the telnet protocol

Defines the twisted protocol classes necessary to establish and control
a telnet client session. Based on the classes in twisted.conch.telnet.
"""

## @package tops.sdss3.tcc.session
# Supports remote operations via the telnet protocol
#
# @author David Kirkby, dkirkby@uci.edu
# @date Created 13-Sep-2008
#
# This project is hosted at http://tops.googlecode.com/

from twisted.conch import telnet

import command

class TelnetException(Exception):
	pass
	
class TelnetSession(telnet.TelnetProtocol,command.CommandQueue):
	"""
	Manages the application-level protocol for a telnet client session.
	
	Subclasses must be customized for a specific telnet host environment
	by setting the values of the following class attributes:
	login_prompt, password_prompt and command_prompt. The per-instance
	username and password are passed in to the class constructor.
	
	A TelnetSession implements an input-driven state machine to perform
	authentication and issue commands. Subclasses can extend this state
	machine following the pattern established here, which requires
	providing a method session_XXX(self,data) for each new state XXX.
	This method will be called when new input data is received in the
	"XXX" state, and can trigger a state change by setting the string
	value of self.state. Subclasses may also want to override the
	session_started() or session_login_failed() methods. Setting
	debug=True is useful for debugging a new subclass as it prints out
	all input and output (except for a user's password).
	
	Users normally interact with a TelnetSession via the asynchronous
	TelnetSession.do() method.
	
	TelnetSession relies on the services of TelnetConnection to handle
	the low-level telnet protocol.
	"""

	# If there are more than this number of commands queued, assume that something
	# is broken and signal an error condition to subsequent command issuers.
	MAX_QUEUED = 10

	registry = { }
	end_of_line = '\n'
	
	@staticmethod
	def do(session_name,command_payload):
		try:
			session = TelnetSession.registry[session_name]
		except KeyError:
			return defer.fail(TelnetException('No such session registered: "%s"' % session_name))
		try:
			return session.add(command_payload)
		except command.CommandException:
			return defer.fail(TelnetException('Command queue overflow for "%s"' % session_name))

	def __init__(self,myname,username,password,debug=False):
		if myname in self.registry:
			raise TelnetException('cannot create second session with name "%s"' % myname)
		self.name = myname
		self.debug = debug
		if self.debug:
			print 'TelnetSession: initializing "%s" (%s)' % (myname,self.__class__.__name__)
		self.registry[myname] = self
		# remember our authentication info
		self.username = username
		self.password = password
		# initialize our state machine
		self.state = 'CONNECTING'
		# initialize our command queue
		command.CommandQueue.__init__(self,self.MAX_QUEUED)
		# telnet.TelnetProtocol has no __init__ method to call

	def send(self,data,secret=False):
		"""
		Writes data through our connection transport
		"""
		if self.debug:
			if secret:
				print 'TelnetSession[%s]: sending something secret' % self.name
			else:
				print ('TelnetSession[%s]: sending %r'
					% (self.name,data.encode('ascii','backslashreplace')))
		self.transport.write(data)

	def dataReceived(self,data):
		"""
		Drives a state machine based on the input received
		"""
		if self.debug:
			print ("TelnetSession[%s]: got %r in state '%s'" %
				(self.name,data.encode('ascii','backslashreplace'),self.state))
		oldState = self.state
		getattr(self, "session_" + self.state)(data)
		if self.debug and self.state != oldState:
			print 'TelnetSession[%s]: entering new state "%s"' % (self.name,self.state)

	def session_CONNECTING(self,data):
		if data.endswith(self.login_prompt):
			self.state = 'AUTHENTICATING'
			self.send(self.username+self.end_of_line)

	def session_AUTHENTICATING(self,data):
		if data.endswith(self.password_prompt):
			self.send(self.password + self.end_of_line,secret=True)
		elif data.endswith(self.login_prompt):
			self.session_login_failed()
		elif data.endswith(self.command_prompt):
			self.session_started()

	def session_started(self):
		"""
		Called when we first get a command line prompt.
		
		This default implementation gets us ready to handle commands.
		Subclasses can override this method to launch a program with its
		own command line interface.
		"""
		self.state = 'COMMAND_LINE_READY'

	def session_login_failed(self):
		"""
		Called if our initial login attempt yields another login prompt.
		
		The default implementation parks our state machine in the
		LOGIN_FAILED state which, by default, is a terminal state.
		Alternatively, you could bump the state machine into the
		'CONNECTING' state which will re-attempt the login handshake
		(but don't do this indefinitely.)
		
		If you do not detect this condition by overriding this method or
		inspecting self.state, your command handlers will never be
		called back and your command queue may fill up.
		"""
		self.state = 'LOGIN_FAILED'

	def session_LOGIN_FAILED(self,data):
		pass
			
	def session_COMMAND_LINE_READY(self,data):
		if self.debug:
			print 'TelnetSession[%s]: ignoring unsolicited data' % self.name
		
	def session_COMMAND_LINE_BUSY(self,data):
		(completed,lines) = self.split_data(data)
		# Append the new lines to the command response.			
		self.command_response.extend(lines)
		# Update our state if necessary
		if completed:
			if self.debug:
				print 'TelnetSession[%s]: response from last command:' % self.name
				for data in self.command_response:
					print repr(data.encode('ascii','backslashreplace'))
			self.state = 'COMMAND_LINE_READY'
			self.done(self.command_response)
	
	def split_data(self,data):
		"""
		Splits received data into lines of command response.
		
		Returns a tuple (completed,lines) where completed is true if the
		data ends with the expected command prompt and lines is an array
		of new lines received with any initial command echo and the
		final command prompt removed.
		"""
		# Break the data into lines
		lines = data.split(self.end_of_line)
		if lines[-1] == '':
			del lines[-1]
		# Ignore a command echo
		if len(self.command_response) == 0 and lines[0] == self.running:
			del lines[0]
		# Have we seen all of the command's response now?
		completed = len(lines) > 0 and lines[-1].endswith(self.command_prompt)
		if completed:
			del lines[-1]
		return (completed,lines)
		
	def issue(self,command):
		"""
		Implements the CommandQueue interface
		"""
		if self.debug:
			print 'TelnetSession[%s]: issuing the command "%s"' % (self.name,command)
		assert(self.state == 'COMMAND_LINE_READY')
		self.state = 'COMMAND_LINE_BUSY'
		self.command_response = [ ]
		self.send(command+self.end_of_line)


class TelnetConnection(telnet.TelnetTransport):
	"""
	Manages the connection-level protocol for a telnet client session.
	
	Application-level data is delegated to a TelnetSession instance.
	"""

	def __init__(self,session_protocol):
		# create a session instance to handle the application-level protocol
		assert(isinstance(session_protocol,TelnetSession))
		self.protocol = session_protocol
		telnet.TelnetTransport.__init__(self)

	def connectionMade(self):
		# propagate our transport instance to the session protocol
		self.protocol.makeConnection(self)


from twisted.internet import protocol,reactor

def prepareTelnetSession(SessionClass,hostname,port=23):
	"""
	Prepares a telnet client session.
	
	SessionClass defines the authentication sequence required and
	handles the application-level protocol. The session does not start
	until the twisted reactor is started.
	"""
	session = protocol.ClientCreator(reactor,TelnetConnection,SessionClass)
	session.connectTCP(hostname,port)
