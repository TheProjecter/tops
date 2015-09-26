# Technology Choices #

Operations software for large scientific facilities such as telescopes, accelerators, and particle detectors has been written many times already, although often in a way that prevents it from being easily adapted to a new environment.

The goal of this project is to re-use or adapt existing software when there is a good match to the (somewhat ill-defined) requirements of SDSS-3 and the existing software is sufficiently well documented and actively supported to lower the overall design and support burden for the lifetime of the SDSS-3 project.

Some notes and impressions of existing software are given below.

## EPICS ##

The [Experimental Physics and Industrial Control System](http://www.aps.anl.gov/epics/) (EPICS) is widely used in particle physics labs and also used, but less extensively, at several observatories including Apache Point.

The core EPICS framework is large and monolithic and so it would be difficult to pick and choose between its components. On the whole, EPICS is better suited to larger projects (as measured by numbers of channels and devices) than SDSS-3, and projects that have more flexibility to replace hardware with supported devices.

However, some of the user-oriented tools developed for EPICS are a good match to SDSS-3 needs and will be evaluated separately: the strip chart and alarm handlers, in particular.

## TUI ##

The [Telescope User Interface](http://www.apo.nmsu.edu/35m_operations/TUI/) (TUI) software used on the Apache Point 3.5m telescope is well documented and already familiar to APO staff. Even better, its author Russ Owen, is available part time to help with integration.

Within the terminology of [this project](DesignOverview.md), TUI is primarily a python application framework that allows the telescope and instruments to be controlled via scripts and Tk displays. TUI embodies a large amount of experience on how to do things efficiently in the control room that must be propagated to the new system.

Devices in TUI are represented by a _model_ that plays a similar role to a [proxy](Proxies.md). Communication with devices is via a _hub_. Some differences in the new design are that each proxy runs as a separate process and communication is via the network fabric and managed by Twisted (see below).

The integration plan for TUI is to adapt its displays and scripting environment to be the core of the [application layer](Applications.md).

## TRON ##

TRON is the hub software that TRON interfaces with on the APO 3.5m telescope. The documentation consists of some text files under svn at `svn://svn.apo.nmsu.edu/tron/tron/trunk/Docs`. Here is a relevant excerpt:
```
What was the original design:

  The original software architecture for 3.5m operations was designed
around the necessity of incorporating heterogeneous, distributed
systems. A simple

What are the problems:

  Remark has served APO very well, and does still work. But it has
  some flaws which are starting to hamper operations:

   - APO does not have the source code. Even if we did, it would be in
   Yerk. So Remark is basically frozen.
   
   - Yerk runs only on Macs.

   - The connection protocol was designed before firewalls, and looks
   for all the world like an enemy attack to the remote institutions.

What are we doing:

  Russell Owen was contracted to write a new GUI interface for the
3.5m operations. The only constraints were that the result be
reasonably platform independant and that the programming language and
style facilitate and even encourage others to modify or extend the
program.

What are we not doing:

  This is a shoestring operation, and we are explicitly not
  redesigning the s/w architecture. We are keeping the simple
  single layer command-response protocol
```
The implementation plan for the new operations software is not to use TRON. Instead, the communication and asynchronous scheduling services of a hub are delegated to the Twisted software package (see below).

## Twisted ##

[Twisted](http://twistedmatrix.com/trac/) is an event-driven network engine written in Python. It is an extensive and mature software project with a [large user base](http://twistedmatrix.com/trac/wiki/ProjectsUsingTwisted). Applications using Twisted include BitTorrent, Zope3 and Justin.tv.

The implementation plan for twisted is to use its transport and protocol layers to manage the asynchronous communications between the process providing operations services. Some services will also use its web layer to serve static and dynamic content.

## Protocol Buffers ##

Although Twisted provides a framework for plug-and-play protocols, it does not define how data is actually packaged for transport. One standard solution to this problem, the [eXtensible Markup Language](http://en.wikipedia.org/wiki/XML) (XML), is widely supported and would probably work, but would likely limit the potential for scaling the new software up to larger systems because its messages are verbose and computationally expensive to parse.

The web development community has been dealing with the same concerns for some time and is converging on an alternative solution, [JavaScript Object Notation](http://en.wikipedia.org/wiki/JSON) (JSON). The name reflects the dominance of Javascript for client-side programming in web browsers, but the actual format is language neutral and reasonably well supported in python.

A third packaging strategy is to use the [protocol buffer infrastructure](http://code.google.com/p/protobuf/) designed by Google and used for all of their client-server communication, which was recently released for public use.

The implementation plan for the new software is to use protocol buffers because of their tight integration with python, proven efficiency and scalability, and support for schema evolution.