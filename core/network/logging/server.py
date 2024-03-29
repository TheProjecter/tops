"""
Implements the server side of distributed logging

The logging server simultaneously handles messages arriving from
producer clients and serves consumer clients via a web server.
"""

## @package tops.core.network.logging.server
# Implements the server side of distributed logging
#
# @author David Kirkby, dkirkby@uci.edu
# @date Created 8-Aug-2008
#
# This project is hosted at sdss3.org and tops.googlecode.com

from twisted.internet.protocol import Factory
from twisted.internet.task import LoopingCall
from twisted.python import log

from collections import deque
from record import *
from datetime import datetime,timedelta

from logging import DEBUG

import logging_pb2

class FeedBuffer(object):
	"""
	Maintains an in-memory buffer of recent log messages.
	"""
	def __init__(self,maxdepth=100):
		self.maxdepth = maxdepth
		self.buffer = deque()
		self.hdr = logging_pb2.Header()
		self.hdr.name = 'logging.server'
		self.msgCount = 0
		self.starttime = datetime.now()
		LoopingCall(self.statusMessage).start(60.0)

	def add(self,record):
		self.buffer.append(record)
		if len(self.buffer) > self.maxdepth:
			self.buffer.popleft()
		self.msgCount += 1

	def dump(self,filt):
		items = ',\n\t'.join([r.json() for r in self.buffer if filt.selects(r)])
		return '({"items":[' + items + ']})'

	def statusMessage(self):
		msg = logging_pb2.Message()
		msg.levelno = DEBUG
		elapsed = datetime.now() - self.starttime
		elapsed = timedelta(elapsed.days,elapsed.seconds)
		msg.body = 'Server has been running %s and handled %u messages.' % (elapsed,self.msgCount) 
		self.add(LogRecord(msg,self.hdr))


from tops.core.network.webserver import WebQuery,prepareWebServer

class FeedUpdate(WebQuery):
	"""
	Serves filtered updates from the site's FeedBuffer via JSON
	responses to HTTP GET queries. Listens to POST queries to configure
	the per-session filter.
	"""
	ServiceName = 'LOGGER'

	def GET(self,request,session,state):
		if not hasattr(state,'filter'):
			print 'cannot serve GET requests before a filter has been specified'
			return '({"items":[]})'
		return session.site.feed.dump(state.filter)
		
	def POST(self,request,session,state):
		sourceFilter = self.get_arg('sourceFilter')
		minLevel = self.get_arg('minLevel')
		if not sourceFilter or not minLevel:
			return 'ERROR'
		else:
			state.filter = LogFilter(sourceFilter,minLevel)
			return 'OK'


from tops.core.network.server import Server

class LogServer(Server):
	"""
	Receives log messages from local and remote clients and feeds them into a central buffer.
	"""
	Header = logging_pb2.Header
	Message = logging_pb2.Message
	
	def handleMessage(self,msg):
		record = LogRecord(msg,self.hdr)
		self.factory.feed.add(record)
		print record


def initialize():
	"""
	Starts the server main loop.
	"""
	from twisted.internet import reactor
	from twisted.python.logfile import LogFile
	import sys
	import os,os.path
	
	# load our run-time configuration
	import tops.core.utility.config as config
	verbose = config.initialize()

	# use file-based logging for ourself (print statements are automatically redirected)
	logpath = config.getfilename('logger','logfile')
	if not logpath or logpath == 'stdout':
		log.startLogging(sys.stdout)
	else:
		(logpath,logfile) = os.path.split(logpath)
		log.startLogging(LogFile(logfile,logpath))

	print 'Executing',__file__,'as PID',os.getpid()
	try:
		# create a record buffer to connect our feed watchers to our clients
		feed = FeedBuffer()

		# initialize socket servers to listen for local and network log message producers
		factory = Factory()
		factory.protocol = LogServer
		factory.feed = feed
		reactor.listenTCP(config.getint('logger','tcp_port'),factory)
		reactor.listenUNIX(config.getfilename('logger','unix_addr'),factory)

		# initialize an HTTP server to handle feed watcher requests via http
		prepareWebServer(
			portNumber = config.getint('logger','http_port'),
			handlers = {"feed":FeedUpdate()},
			properties = {"feed":feed},
			filterLogs = True
		)

		# fire up the reactor
		print 'Waiting for clients...'
		reactor.run()
		
	except Exception:
		print 'Reactor startup failed'
		# How do I release my unix socket cleanly here?
		#reactor.stop()
		raise

if __name__ == '__main__':
	initialize()
