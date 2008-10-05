"""
Parses tcl code to generate web documentation

Designed for semantic analysis of the SDSS legacy IOP code. Uses the PLY
lexical analyzer (http://www.dabeaz.com/ply/) Run with option --help for
usage info.
"""

## @package tops.sdss3.design.iop
# Parses the IOP tcl code to generate web documentation
#
# @author David Kirkby, dkirkby@uci.edu
# @date Created 1-Oct-2008
#
# This project is hosted at http://tops.googlecode.com/

class EndOfTokens(Exception):
	pass
	
class FatalParseError(Exception):
	pass

import ply.lex as lex

class LexicalAnalyzer(object):
	"""
	Splits a tcl file into parsing tokens based on a lexical analysis
	
	Uses the PLY lexer to do the hard work.
	"""
	# list the single-character literal tokens we care about
	literals = '{}#$"\[\];'

	# list the non-literal token types defined below
	tokens = ('WS','EOL','WORD')

	# inline whitespace
	t_WS = r'[ \t]+'

	# collapse multiple newlines separated by whitespace into a single EOL token
	t_EOL = r'\n[ \t\n]*'

	# Define a TCL word as a sequence of non-whitespace characters excluding the literals above
	# unless they are escaped.
	t_WORD = r'([^%s\\ \t\n]|(\\.))+' % (literals)

	def t_error(self,t):
		raise FatalParseError("Illegal character on line %d: '%s'" % (1+t.lineno,t.value))

	def __init__(self):
		self.lexer = lex.lex(object=self)

from tops.core.utility.html import *

class File(object):
	"""
	Prepares a tcl file for parsing
	
	The title and base will be used in HTML output.

	A debug level of 0 is silent unless there is a fatal error. Level 2
	prints the line numbers where each parsing unit begins and ends.
	Level 3 also prints each token.
	"""
	def __init__(self,name,title,base,lexer,debug=0):
		self.data = ''
		self.offsets = [ ]
		self.escapes = [ ]
		offset = 0
		for line in open(name):
			self.offsets.append(offset)
			offset += len(line)
			if line[-2:] == '\\\n':
				if debug > 1:
					print 'removing escaped newline at end of line',len(self.offsets)
				# replace an escaped newline with two spaces to preserve offsets
				self.data += line[:-2]
				self.data += '  '
				self.escapes.append(offset-2)
			else:
				self.data += line
		self.nlines = len(self.offsets)
		self.lexer = lexer
		self.title = title
		self.base = base
		self.debug = debug
		self.last_line = 0
		self.script = None

	def lineno(self,offset=None):
		"""
		Returns the line number in the input file for the given offset
		
		Because of escaped-newline processing, line numbers in the
		parsed stream can be different from those returned here. If no
		offset is provided, uses the offset where the next token will
		start.
		"""
		if not offset:
			offset = self.lexer.lexpos
		# continue from the last line unless we have gone backwards
		if offset >= self.offsets[self.last_line]:
			line = self.last_line
		else:
			line = 0
		# scan forwards to find which line the offset is on
		while line < self.nlines and offset >= self.offsets[line]:
			line += 1
		self.last_line = line - 1
		return line
		
	def next_token(self):
		"""
		Returns the next token from the file
		
		Raises an EndOfTokens exception if there are no more tokens
		available. The returned token will have a lineno and value set
		as if there had been no escaped-newline processing of the file.
		"""
		token = self.lexer.token()
		if not token:
			raise EndOfTokens
		# store this token's line number based on its file offset
		token.lineno = self.lineno(token.lexpos)
		# undo any escaped-newline substitution applied to this token's value
		start = token.lexpos
		end = start + len(token.value)
		for offset in self.escapes:
			if offset < start or offset >= end:
				continue
			pos = offset - start
			token.value = token.value[:pos] + '\\\n' + token.value[pos+2:]
			if self.debug > 1:
				print 'restored escaped newline at end of line',token.lineno
			break
		# print out each token if we are being verbose
		if self.debug > 2:
			print 'shift',token
		return token
		
	def parse(self):
		"""
		Parses this file and returns a Script object
		
		Raises a FatalParseError exception if there is a problem.
		"""
		if self.debug:
			print 'parsing %s (%d lines)' % (self.title,self.nlines)
		self.lexer.input(self.data)
		try:
			self.script = Script(self,self.debug)
			return self.script
		except FatalParseError,e:
			print 'ERROR:',e
			
	def export(self,filename,index,stylesheet):
		if not self.script:
			print 'file has not been successfully parsed yet, nothing to export'
			return
		doc = HTMLDocument(
			Head(title=self.title,base={'href':self.base},css=stylesheet),
			Body(H1(self.title),index,Div(id='content'))
		)
		self.script.export(doc['content'])
		f = open(filename,'w')
		print >> f,doc
		f.close()

class Parser(object):
	"""
	Provides common functionality needed by all language element parsers
	"""	
	prefix = ''
	suffix = ''

	def __init__(self,tokenizer,debug,info=''):
		self.tokenizer = tokenizer
		self.debug = debug
		self.tokens = [ ]
		self.name = self.__class__.__name__
		if debug > 1:
			print 'line %4d: %s begin %s' % (tokenizer.lineno(),self.name,info)
		self.parse(debug)
		if debug > 1:
			print 'line %4d: %s end   %s' % (tokenizer.lineno(),self.name,info)

	def __repr__(self):
		return '%s%s' % (self.name,str(self.tokens))

	def next(self,end_is_fatal=True):
		"""
		Returns the next token
		
		Raises a fatal error if end_is_fatal is True (the default) and
		there are no more tokens available. Stores the lexical tokens
		read by this instance in the stream array.
		"""
		try:
			self.last_token = self.tokenizer.next_token()
			return self.last_token
		except EndOfTokens:
			if end_is_fatal:
				raise FatalParseError('unexpected EOF in %s' % self.name)
			else:
				raise

	def token_stream(self):
		"""
		Returns the list of tokens associated with this parsing object
		
		Works recursively on any embedded parsing objects to flatten the
		token stream that is returned and only return LexToken objects.
		Our own prefix or suffix tokens, if any, are not included but
		those of any descendents are.
		"""
		stream = [ ]
		for tok in self.tokens:
			# emit a lexical token directly
			if isinstance(tok,lex.LexToken):
				stream.append(tok)
			else:
				# emit parsed object's prefix token, if any
				if tok.prefix_token:
					stream.append(tok.prefix_token)
				# let the parsed object emit its own content tokens
				stream.extend(tok.token_stream())
				# emit parsed object's suffix token, if any
				if tok.suffix_token:
					stream.append(tok.suffix_token)
		return stream

	def reconstruct(self):
		"""
		Reconstructs the string that was parsed to create this instance
		
		Sublcasses should provide appropriate values for the prefix and
		suffix class attributes to define their wrapper tokens.
		"""
		data = self.prefix
		for token in self.tokens:
			if isinstance(token,Parser):
				data += token.reconstruct()
			else:
				data += token.value
		data += self.suffix
		return data
		
	def export(self,container):
		"""
		Fills the DOM container with an HTML description of this instance
		"""
		content = Span(className=self.name)
		if self.prefix:
			content.append(self.prefix)
		for token in self.tokens:
			if isinstance(token,Parser):
				token.export(content)
			elif isinstance(token,lex.LexToken):
				# is this literal tagged?
				if hasattr(token,'tag'):
					content.append(Span(token.value,id=token.tag,className='tagged'))
				else:
					content.append(token.value)
			else:
				print 'export: ignoring illegal token "%s"' % token
		if self.suffix:
			content.append(self.suffix)
		container.append(content)
		
	def append(self,type_or_value,*type_args):
		"""
		Appends a new token of the specified type or value
		"""
		if isinstance(type_or_value,type) and issubclass(type_or_value,Parser):
			# we are appending a new Parser instance
			(prefix,suffix) = (None,None)
			if type_or_value.prefix:
				# capture the token that triggered this new Parser instance
				prefix = self.last_token
				assert(prefix.value == type_or_value.prefix)
			# create the new Parser instance (the ctor actually does the parsing)
			parsed = type_or_value(self.tokenizer,self.debug,*type_args)
			if type_or_value.suffix:
				# capture the token that ended this new Parser instance
				suffix = parsed.last_token
				assert(suffix.value == type_or_value.suffix)
			# record the prefix and suffix tokens in the new instance
			parsed.prefix_token = prefix
			parsed.suffix_token = suffix
			self.tokens.append(parsed)
		elif isinstance(type_or_value,lex.LexToken):
			self.tokens.append(type_or_value)
		else:
			raise FatalParseError('append: unrecognized token type: %r' % type_or_value)
			
	def embed(self):
		"""
		Re-parses this object as an embedded self-contained script
		"""
		if self.debug > 1:
			print 're-parsing %s as an embedded script' % self.name
		try:
			embedded = EmbeddedScript(self.tokenizer,self.debug,parent=self)
			self.tokens[:] = [embedded]
		except FatalParseError,e:
			if self.debug:
				print 're-parsing of %s as embedded script failed: %s' % (self.name,e)

class Script(Parser):
	"""
	Represents a tcl script consisting of a sequence of Commands
	"""
	def parse(self,debug):
		try:
			while True:
				self.append(Command)
		except EndOfTokens:
			pass
			
class EmbeddedScript(Script):
	"""
	Represents a complete script embedded within a parse object
	
	The embedded script is built by replaying the lexical tokens of
	the specified parent parse object.
	"""
	def __init__(self,tokenizer,debug,parent):
		# we re-use our parent's token stream as our input source
		self.source = parent.token_stream()
		self.index = 0
		# we take over the tokenizer's job ourself
		self.title = tokenizer.title
		Script.__init__(self,tokenizer=self,debug=debug)
		
	def lineno(self):
		"""
		Returns the line number corresponding to the next token
		"""
		try:
			return self.source[self.index].lineno
		except IndexError:
			try:
				return self.source[-1].lineno
			except IndexError:
				return -1
			
	def next_token(self):
		"""
		Returns the next token or raises EndOfTokens
		"""
		try:
			token = self.source[self.index]
			self.index += 1
			if self.debug > 2:
				print 'shift',token
			return token
		except IndexError:
			raise EndOfTokens()
	
class Command(Parser):
	"""
	Represents a tcl command
	
	A commmand is either a Comment or a sequence of words, each
	represented by a string, Variable, Substitution, Quoted, or Group.
	The whitespace between words is preserved so that the original file
	can be exactly reconstructed after parsing.
	"""
	def parse(self,debug):
		while True:
			try:
				token = self.next(end_is_fatal=False)
			except EndOfTokens:
				if len(self.tokens) > 0:
					if debug > 1:
						print 'non-empty final line is missing \\n'
					break
				else:
					raise
			if token.type in ('EOL',';'):
				self.append(token)
				break
			elif token.type == '#':
				# only white space can precede a valid comment
				is_comment = True
				for tok in self.tokens:
					if not isinstance(tok,lex.LexToken):
						is_comment = False
						break
					if not tok.type in ('WS','EOL'):
						is_comment = False
						break
				if is_comment:
					self.append(Comment)
					break
				else:
					if debug:
						print 'found non-comment # in command on line %d' % token.lineno
					self.append(token)
			elif token.type == '$':
				self.append(Variable)
			elif token.type == '[':
				self.append(Substitution)
			elif token.type == '"':
				self.append(Quoted)
			elif token.type == '{':
				self.append(Group)
			elif token.type == '}':
				raise FatalParseError('unexpected } on line %d during Command' % token.lineno)
			elif token.type == ']':
				raise FatalParseError('unexpected ] on line %d during Command' % token.lineno)
			else:
				self.append(token)
		# extract the words of this command, if any, ignoring whitespace and comments,
		# and any final semicolon
		words = [ ]
		for tok in self.tokens:
			if isinstance(tok,lex.LexToken) and tok.type in ('WS','EOL',';'):
				continue
			if isinstance(tok,Comment):
				continue
			words.append(tok)
		if len(words) == 0:
			return
		# do we have a literal base word?
		if not isinstance(words[0],lex.LexToken) or words[0].type != 'WORD':
			return
		baseword = words[0].value
		# should we do any further processing of this command?
		if baseword == 'proc':
			# Process a tcl 'proc' command: http://www.tcl.tk/man/tcl8.4/TclCmd/proc.htm
			# a proc command should always have 4 words
			if len(words) != 4:
				if debug:
					print ('ignoring "proc" with %d words (expected 4) on line %d'
						% (len(words),words[0].lineno))
				return
			# expand the procedure body if it is a Group
			#if isinstance(words[3],Group):
			#	words[3].embed()
			# do we have a literal proc name?
			if not isinstance(words[1],lex.LexToken) or words[1].type != 'WORD':
				if debug:
					print 'ignoring "proc" with computed name on line %d' % words[0].lineno
				return
			# record this procedure definition in the global dictionary
			proc_name = words[1].value
			title = self.tokenizer.title
			if proc_name in self.dictionary:
				self.dictionary[proc_name].append(title)
				tag = "%s_%d" % (proc_name,len(self.dictionary[proc_name]))
				if debug:
					print ('added duplicate %d of "%s" to command dictionary on line %d'
						% (len(self.dictionary[proc_name]),proc_name,words[0].lineno))
			else:
				self.dictionary[proc_name] = [ title ]
				tag = proc_name
				if debug > 1:
					print 'added "%s" to command dictionary on line %d' % (proc_name,words[0].lineno)
			# tag the procedure name for our HTML markup
			words[1].tag = tag
	"""
	Initialize a dictionary to capture all tcl procedure definitions we
	find. Keys are procedure names with an array of file titles as the
	corresponding value. Note that a tcl procedure of the same name can
	be defined more than once, even in the same file.
	"""
	dictionary = { }

	@staticmethod
	def build_index(title=None):
		"""
		Returns an HTML index of tcl command procedures
		
		The index will be alphabetical. If title is specified, only
		procedures defined within a file having a matching title will be
		included. If a procedure is defined in the specified file but
		also in other files, links to all files where the procedure is
		defined will be included in the generated index. Returns a DIV
		element with class='index'.
		"""
		index = Div(className='index')
		first_letter = '?'
		for proc in sorted(Command.dictionary,key=str.lower):
			titles = Command.dictionary[proc]
			if not title or title in titles:
				if proc[0].upper() != first_letter:
					first_letter = proc[0].upper()
					index.append(
						Div(Entity('mdash'),' ',first_letter,' ',Entity('mdash'),className='letter')
					)
				for (k,f) in enumerate(titles):
					target = f.replace('.tcl','.html')
					if k == 0:
						link = A(proc,href="%s#%s" % (target,proc))
						index.extend([' ',link])
					else:
						link = A('[',k+1,']',href="%s#%s_%d" % (target,proc,k+1))
						index.extend([Entity('nbsp'),link])
		return index

class Comment(Parser):
	"""
	Represents a tcl comment
	
	Comments begin with a '#' symbol where the start of a new command is
	expected, and end with the first un-escaped newline.
	"""
	prefix = '#'
	
	def parse(self,debug):
		while True:
			token = self.next()
			self.append(token)
			if token.type == 'EOL':
				break

class Quoted(Parser):
	"""
	Represents a tcl quoted word delimeted by double quotes
	
	The word contents will be parsed to detect any embedded command or
	variable substitutions, or embedded groups.
	"""	
	prefix = '"'
	suffix = '"'

	def parse(self,debug):
		while True:
			token = self.next()
			if token.type == '$':
				self.append(Variable)
			elif token.type == '[':
				self.append(Substitution)
			elif token.type == '{':
				self.append(Group)
			elif token.type == '}':
				raise FatalParseError('unexpected } on line %d during Quoted' % token.lineno)
			elif token.type == ']':
				raise FatalParseError('unexpected ] on line %d during Quoted' % token.lineno)
			elif token.type == '"':
				break
			else:
				self.append(token)

class Group(Parser):
	"""
	Represents a tcl group delimited by { }
	
	Groups are considered opaque words in tcl so no command or variable
	substitutions will be detected within a group. However, any embedded
	'{' must be balanced by a closing '}' within the group. This is
	accomplished here by creating a nested Group for each '{' even
	though this is not semantically meaningful (since the top-level
	group is an entire tcl word) and is applied to non-group constructs
	like ${variable}.
	"""
	prefix = '{'
	suffix = '}'
	
	def __init__(self,tokenizer,debug,depth=1):
		self.depth = depth
		info = '-'*depth + ('> %2d' % depth)
		Parser.__init__(self,tokenizer,debug,info)
	
	def parse(self,debug):
		while True:
			token = self.next()
			if token.type == '{':
				self.append(Group,self.depth+1)
			elif token.type == '}':
				break
			else:
				self.append(token)

class Substitution(Parser):
	"""
	Represents a tcl command substitution delimited by [ ]
	"""
	prefix = '['
	suffix = ']'
	
	def parse(self,debug):
		while True:
			token = self.next()
			if token.type == ']':
				break
			elif token.type == '[':
				self.append(Substitution)
			elif token.type == '{':
				self.append(Group)
			elif token.type in ('EOL','}'):
				raise FatalParseError('unexpected Substitution token %s' % token)
			else:
				self.append(token)
		# now that we have captured the whole substitution text, try to
		# re-parse it as an embedded script
		self.embed()

class Variable(Parser):
	"""
	Represents a tcl variable substition starting with $
	
	Completely captures the $name and ${name} forms, but will generally
	only capture the beginning of $name(index) - up to the first white
	space in 'index'. The main purpose of this parser is to distinguish
	between '{' used to start a group and '${' used to start a variable
	substitution.
	"""
	prefix = '$'
	
	def parse(self,debug):
		while True:
			token = self.next()
			if token.type == '{':
				if len(self.tokens) == 0:
					self.append(token)
					while True:
						token = self.next()
						self.append(token)
						if token.type == '}':
							break
					break
				else:
					raise FatalParseError('unexpected { in Variable on line %d' % token.lineno)
			elif token.type == 'WORD':
				# will match $name and part or all of $name(index)
				self.append(token)
				break
			else:
				raise FatalParseError('unexpected token %s in Variable' % token)
			

import sys
import os,os.path
import shutil

def main():

	from optparse import OptionParser

	# parse command-line options
	options = OptionParser(usage = 'usage: %prog [options] source')
	options.add_option("-d","--debug",type="int",metavar="INT",
		help="debug printout level (0=none, default is %default)")
	options.add_option("-o","--output",metavar="PATH",
		help="output path (created if necessary, omit for no output)")
	options.add_option("-R","--recursive",action="store_true",
		help="recursively visit all source tcl files (%default by default)")
	options.add_option("--title",
		help="title to use for master index web page (default is %default)")
	options.set_defaults(debug=0,recursive=False,title='Command Index')
	(opts,args) = options.parse_args()

	# validate command-line options
	if opts.debug:
		print 'debug level is %d' % opts.debug
	if len(args) != 1:
		options.print_help()
		sys.exit(-1)
	source = args[0]
	if not os.path.exists(source):
		print 'no such source: %s' % source
		sys.exit(-2)

	# one-time initialization of lexical analyzer
	lexer = LexicalAnalyzer().lexer
	
	# the list of files we have parsed
	parsed_files = [ ]
	
	# parse the source files
	if os.path.isfile(source):
		# process a single file
		title = os.path.basename(source)
		f = File(source,title,'',lexer,opts.debug)
		f.parse()
		parsed_files.append(f)
	else:
		# walk through the source tree
		for (root,dirs,files) in os.walk(source):
			if not opts.recursive:
				del dirs[:]
			# calculate the output path relative to the command-line 'source'
			# and the return path to the source
			(ipath,opath,rpath) = (root,'','')
			while not os.path.samefile(ipath,source):
				(ipath,segment) = os.path.split(ipath)
				opath = os.path.join(segment,opath)
				rpath = os.path.join(rpath,'..')
			# loop over files in this source directory
			for filename in files:
				# we are only interested in tcl files
				(base,ext) = os.path.splitext(filename)
				if ext != '.tcl':
					continue
				name = os.path.join(root,filename)
				title = os.path.join(opath,filename)
				f = File(name,title,rpath,lexer,opts.debug)
				f.parse()
				parsed_files.append(f)
	if not opts.output:
		sys.exit(0)
	# create the output path if necessary
	if not os.path.isdir(opts.output):
		if opts.debug:
			print 'creating output directory',opts.output
		os.makedirs(opts.output)
	# copy our stylesheet to the output directory
	module_path = os.path.dirname(__file__)
	stylesheet = 'tclcode.css'
	shutil.copyfile(os.path.join(module_path,stylesheet),os.path.join(opts.output,stylesheet))
	# write out a master index file if we parsed multiple files
	if len(parsed_files) > 1:
		if opts.debug:
			print 'writing master index with title "%s"' % opts.title
		doc = HTMLDocument(
			Head(title=opts.title,css=stylesheet),
			Body(H1(opts.title),Command.build_index())
		)
		f = open(os.path.join(opts.output,'index.html'),'w')
		print >> f,doc
		f.close()
	# write out each source file with its own index
	for f in parsed_files:
		(root,ext) = os.path.splitext(f.title)
		filename = os.path.join(opts.output,root)
		filename += '.html'
		dirname = os.path.dirname(filename)
		if not os.path.isdir(dirname):
			if opts.debug:
				print 'creating',dirname
			os.makedirs(dirname)
		index = Command.build_index(f.title)
		if opts.debug:
			print 'writing',filename
		f.export(filename,index,stylesheet)


if __name__ == '__main__':

	main()
	
