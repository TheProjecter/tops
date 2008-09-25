"""
Parses the message format generated by the TCC interpreter
"""

## @package tops.sdss3.tcc.message
# Parses the message format generated by the TCC interpreter
#
# @author David Kirkby, dkirkby@uci.edu
# @date Created 23-Sep-2008
#
# This project is hosted at http://tops.googlecode.com/

## Primitive patterns defined without any capturing groups
patterns = {
	'unsigned':		'0|[1-9][0-9]*',
	'hex':			'0x[0-9a-f]+',
	'string':		r'"(?:[^"\\]|\\.)*"',
	'pname':		'[A-Za-z0-9_]+',
	'from':			'\[from[^\]]+\]',
	'status':		'[\:IWF>]'
}

# Compound patterns defined without any capturing groups:

# - A floating-point decimal number without exponent
patterns['decimal'] = '[-+]?(?:(?:(?:%(unsigned)s)(?:\.[0-9]*)?)|(?:\.[0-9]+))' % patterns

# - A flooating-point decimal number with an optional exponent that might also be NaN
patterns['float'] = '(?:(?:%(decimal)s)(?:[eE][-+]?[0-9]+)?)|NaN' % patterns

# - A hex or decimal number
patterns['number'] = '(?:%(hex)s)|(?:%(float)s)' % patterns

# - A parameter value which is either a number or a string
patterns['pvalue'] = '(?:%(number)s)|(?:%(string)s)' % patterns

# - An array of one or more parameter values separated by commas.
patterns['array'] = '(?:%(pvalue)s)(?:\s*,\s*(?:%(pvalue)s))*' % patterns

# - A parameter declaration (which might not have an assignment)
patterns['passign'] = '(?:%(pname)s)(?:\s*=\s*(?:%(array)s))?' % patterns

# - A sequence of one or more parameter declarations separated by semicolons.
patterns['pseq'] = '(?:%(passign)s)(?:\s*;\s*(?:%(passign)s))*' % patterns

# A complete interpreter message line with capturing groups
patterns['msg'] = '\r?(%(unsigned)s) (%(unsigned)s) (%(status)s)\s+(%(pseq)s)?(?:\s*%(from)s)?' % patterns


class MessageError(Exception):
	pass

# TCC status codes from src/subr/msg/format.for
status_codes = {
	':': 'Done',    # also 'Superceded'
	'>': 'Started',
	'I': 'Information',
	'W': 'Warning',
	'F': 'Error',
	'!': 'Fatal'
}	

# compiled regular expressions used by the parser
import re
msgScanner = re.compile('%(msg)s$' % patterns)
declSplitter = re.compile('%(passign)s' % patterns)

def parse(line):
	"""
	Attempts to parse a line of text as a TCC message.
	"""
	parsed = msgScanner.match(line)
	if not parsed:
		raise MessageError('badly formed line: %s' % line)
	if parsed.end() < len(line):
		raise MessageError('unexpected trailing characters: %s' % line)
	(mystery_num,user_num,status,pseq) = parsed.groups()
	if status in status_codes:
		status = status_codes[status]
	# The line might not have any parameter values, e.g.
	# 0 3 : [from 'gcamera status' and 'broadcast...']
	if not pseq:
		return (mystery_num,user_num,status,pseq)
	# split up the parameter declaration sequence
	declarations = declSplitter.split(pseq)
	return (mystery_num,user_num,status,declarations)

import unittest

class MessageTests(unittest.TestCase):

	def check(self,p,text,valid):
		m = p.match(text)
		matched = m and m.end() == len(text)
		if valid and not matched:
			raise Exception("'%s' does not match '%s'" % (text,p.pattern))
		elif not valid and matched:
			raise Exception("'%s' should not match '%s'" % (text,p.pattern))

	def test00(self):
		"""Valid unsigned integers"""
		p = re.compile("%(unsigned)s$" % patterns)
		for text in ['0','1','12','120','102']:
			self.check(p,text,True)

	def test01(self):
		"""Invalid unsigned integers"""
		p = re.compile("%(unsigned)s$" % patterns)
		for text in ['abc','00','01','001','-1','-0']:
			self.check(p,text,False)

	def test02(self):
		"""Valid floating-point numbers"""
		p = re.compile("%(float)s$" % patterns)
		for text in [
			'0','1','12','120','102','1.','-1','+.3','-1.','0.23','1e1','1e-1','-1e+1','.2','-.2'
		]:
			self.check(p,text,True)

	def test03(self):
		"""Invalid floating-point numbers"""
		p = re.compile("%(float)s$" % patterns)
		for text in ['abc','0e','e0','1.2.3','1e-+2','+1-2']:
			self.check(p,text,False)

	def test04(self):
		"""Valid double-quoted string literals"""
		p = re.compile("%(string)s$" % patterns)
		for text in ['""','"a"','"abc"','";"',r'"spawn \"show users\""']:
			self.check(p,text,True)

	def test05(self):
		"""Invalid double-quoted string literals"""
		p = re.compile("%(string)s$" % patterns)
		for text in ["'abc'",'abc','"a"bc','ab"c"']:
			self.check(p,text,False)

	def test06(self):
		"""Valid array of numeric values"""
		p = re.compile("%(array)s$" % patterns)
		for text in ['1.2','1.2,3.4','0','0xdeadbeef','0x123 ,-1.23','4728232973.56']:
			self.check(p,text,True)

	def test07(self):
		"""Invalid array of numeric values"""
		p = re.compile("%(array)s$" % patterns)
		for text in ['1.2,',',1.2','1.2,3.4,']:
			self.check(p,text,False)

	def test08(self):
		"""Valid parameter assignment"""
		p = re.compile("%(passign)s$" % patterns)
		for text in [
			'Text="827800 packets sent successfully"',
			'UT1=  4728232973.56',
			'AzStat=121.000050, 0.000000, 4728233002.17664, 0x00003800',
			'BadRotStatus',
			'Cmd="convert 30,45 FK5=2000.0 Galactic"',
			'TCCStatus="HHH","NNN"',
			'ObjInstAng = NaN, NaN, NaN',
			r'Cmd="spawn \"show users\""'
		]:
			self.check(p,text,True)

	def test09(self):
		"""Invalid parameter assignment"""
		p = re.compile("%(passign)s$" % patterns)
		for text in ['1.2,',',1.2','1.2,3.4,']:
			self.check(p,text,False)

	def test10(self):
		"""Valid parameter assignment sequences"""
		p = re.compile("%(pseq)s$" % patterns)
		for text in [
			'TCCStatus="HHH","NNN"; TCCPos=NaN,NaN,NaN; AxePos=121.00,30.00,0.00',
			'AxisErrCode="HaltRequested","HaltRequested","HaltRequested"',
			'AzStat=121.000050, 0.000000, 4728233002.17664, 0x00003800',
			'PrimF_BFTemp=   10.00,    0.00; SecF_BFTemp=   10.00,    0.00',
			'Cmd="convert 30,45 FK5=2000.0 Galactic"'
		]:
			self.check(p,text,True)

	def test11(self):
		"""Invalid parameter assignment sequences"""
		p = re.compile("%(pseq)s$" % patterns)
		for text in ['1.2,',',1.2','1.2,3.4,']:
			self.check(p,text,False)

	def test12(self):
		"""Valid messages"""
		p = re.compile("%(msg)s$" % patterns)
		for text in [
			'0 3 : Cmd="axis status all"',
			"0 3 : [from 'gcamera status' and 'broadcast...']",
			'0 3 : Cmd="convert 30,45 FK5=2000.0 Galactic"',
			'0 3 F Failed; Cmd="gmech status"',
			'0 3 : Cmd="mirror status"',
			'0 3 : Cmd="process status"',
			'0 3 : Text="No job running" [from \'queue status\']',
			'0 3 : Text="Show Users"',
			r'0 3 : Cmd="spawn \"show users\""',
			'0 3 : Cmd="wait 1.5"'
		]:
			self.check(p,text,True)

	def test13(self):
		"""Invalid messages"""
		p = re.compile("%(msg)s$" % patterns)
		for text in ['1.2,',',1.2','1.2,3.4,']:
			self.check(p,text,False)

if __name__ == '__main__':
	unittest.main()
