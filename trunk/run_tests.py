"""
Finds and runs unit tests

Finds unit tests by recursively searching from the current directory.
Tests are loaded and run using the standard unittest infrastructure. Any
directories or files that should not be searched can be added to the
ignored array. All other .py files will be imported as part of searching
for tests, so beware of any import side effects or conflicts from
importing all modules at once.

TODO:
 - prevent duplicate tests from pkg caused by 'from pkg import *'
"""

## @package tops.run_tests
# Finds and runs unit tests
#
# @author David Kirkby, dkirkby@uci.edu
# @date Created 6-Sep-2008
#
# This project is hosted at http://tops.googlecode.com/

import os
import sys
import time
import unittest

# This file is assumed to be in the top-level directory of the module
# tree to be tested. Use this assumption to determine our package
# name and top-level path.

if __name__ == '__main__':
	__file__ = sys.argv[0]
	
(mypath,myname) = os.path.split(os.path.abspath(__file__))
mypkg = os.path.basename(mypath)

# directories and files to ignore
ignored = [myname,'.svn']

suite = unittest.TestSuite()

def path_to_module(name):
	"""
	Returns an absolute path converted to a module name under the mypkg tree.
	"""
	module = [ ]
	while name:
		if name == mypath:
			module.append(mypkg)
			break
		(name,base) = os.path.split(name)
		module.append(base)
	module.reverse()
	return '.'.join(module)

def visit(arg,dirname,names):
	"""
	Visits a directory under mypath, importing any .py files and adding
	any unit tests found to our test suite.
	"""
	# is this a python module?
	if not '__init__.py' in names:
		del names[:]
		return
	dotpath = path_to_module(dirname)
	print dotpath
	for (index,name) in enumerate(names):
		if name in ignored:
			del names[index]
		elif name[-3:] == '.py':
			dotname = '%s.%s' % (dotpath,name[:-3])
			tests = unittest.defaultTestLoader.loadTestsFromName(dotname)
			print '  %-40s ... %3d test cases' % (dotname,tests.countTestCases())
			suite.addTest(tests)

# print test environment info
print '## Running %s on %s' % (myname,time.ctime(time.time()))
print sys.version

# find all tests
print '\n## Scanning for tests in the module tree of "%s" from %s' % (mypkg,mypath)
os.path.walk(mypath,visit,None)

# run all tests
print '\n## Running tests'
test_runner = unittest.TextTestRunner(descriptions=2,verbosity=1)
result = test_runner.run(suite)
if result.failures or result.errors:
	sys.exit(1)
