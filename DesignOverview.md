# Overview of the Operations Software Design #

The operations software is designed as three horizontal layers that interface the system's users to its hardware devices:
  * Sessions: the interface between users and applications.
  * Applications: the GUI and scripting environment that users interact with.
  * [Proxies](Proxies.md): the interface between applications and hardware devices.
These layers are vertically integrated with the following operations infrastructure:
  * [Logging](Logging.md): the destination for all text-based data.
  * [Archiving](Archiving.md): the destination for all numeric data.
  * [Configuration](RuntimeConfig.md): management of the run-time configuration for operations services.
  * [Process Control](Running.md): monitoring and control of the co-operating processes that provide operations services.
  * File Handling: assembling and transporting the potentially large files produced during operations.
The distinction between logging and archiving is [explained here](Dataflow.md).

The following block diagram illustrates the relationships between these components:

![http://tops.googlecode.com/svn/wiki/images/BlockDiagDesign.png](http://tops.googlecode.com/svn/wiki/images/BlockDiagDesign.png)

For more detailed information about the overall design, refer to the links above and the background material below.

For information about what is actually implemented today, refer to the [release notes](ReleaseNotes.md).

## Background Material ##

Links to some SDSS-3 presentations on the new software design:

  * [Design documents](http://positron.ps.uci.edu/~dkirkby/sdss3-17Jul08/) (state diagrams, use cases) from 17 Jul 2008.
  * [MARVELS proxy design notes](http://positron.ps.uci.edu/~dkirkby/marvels-27Jun08/) from 27 Jun 2008.
  * [Conceptual design overview](http://positron.ps.uci.edu/~dkirkby/home/docs/SDSS3-Ops-ConceptualDesign.pdf) (pdf) from 5 Jun 2008.