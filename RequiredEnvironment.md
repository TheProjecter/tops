# The Required Operations Software Environment #

The operations software depends on other software that is listed below. Examples of platforms where the software is known to work are [listed here](Platforms.md).

## Python ##

Python 2.5 is required, although the only thing that breaks 2.4 is a few conditional expressions (x = a if b else c), so this could be relaxed without too much trouble if necessary. Currently using 2.5.2 on all platforms.

## Python Libraries ##

  * zope.interface : Needed for twisted. Using 3.3.0 and 3.4.1, but twisted should also work with older versions.
  * twisted : Provides our low-level networking framework. Using 8.1.0.
  * google.protobuf : Provides our network serialization framework. Using 2.0.0 and 2.0.1.
  * pycrypto: Provides encryption of private data. Using 2.0.1.

## Code Management ##

Code is hosted at http://tops.googlecode.com/

Using svn 1.2.3 and 1.4.4.

SVN needs to be configured with the SSL repository access module for write access to the repository (developers must also be registered with the TOPS google code project), but the basic SVN installation works fine for read-only checkout and installation.

## Build System ##

Using SConstruct v1.0.1. It would be relatively easy to install the software without SConstruct by copying the protocol buffer python files from another installation. See the [installer's guide](InstallersQuickStart.md) for details.

## Browser ##

The operations web interfaces require a reasonably modern browser with cookies and javascript enabled. Examples of browsers where this is known to work are [listed here](Platforms.md).