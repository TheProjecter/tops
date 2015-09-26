# Release Notes for Tagged Versions of The Operations Software #

In reverse chronological order...

## V0.5 ##

Created 06-Oct-2008.

This is the last release for active development on tops.googlecode.com and the initial release imported to sdss3.org.

The main new functionality is a TCL parser for automated analysis of the SDSS-3 IOP legacy code in the module tops.sdss3.design.iop.tclparser.

## V0.4 ##

Created 25-Sep-2008.

Provides the basic infrastructure (logging, archiving, process startup, and run-time configuration) and working read-only examples of the proxies that interface with the TCC via its UDP broadcasts (tcc.listener) and interactive interpreter (tcc.session).

Solid outlines in the block diagram below show exactly which components are implemented in this version:

![http://tops.googlecode.com/svn/wiki/images/BlockDiagV04.png](http://tops.googlecode.com/svn/wiki/images/BlockDiagV04.png)

## V0.3 ##

Created 11-Sep-2008.

Includes functional logging and archiving services and the TCC listener proxy. Requires that the google.protobuf python library has been installed and provides an scons build script. Tested on the 2.5m subnet at APO.

## V0.2 ##

Created 9-Sep-2008.

Test core client-server networking. Requires that the zope.interface and twisted python libraries have been installed.

## V0.1 ##

Created 9-Sep-2008.

Basic install test. Should only require that python 2.5 is installed.