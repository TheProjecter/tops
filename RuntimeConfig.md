# Configuring the Operations Software #

The operations software obtains the configuration data it needs at run time by reading text files in the standard [INI format](http://en.wikipedia.org/wiki/INI_file). A more 'modern' approach would be to use XML files but we do not need an arbitrary hierarchy here and prefer a format that is easier for humans to edit directly. The INI format is actually not very well standardized so, for the definitive reference of what works here, refer to the documentation of the [ConfigParser library](http://docs.python.org/lib/module-ConfigParser.html) that this software uses.

The operations software makes a distinction between _core_ software and _project_ software, and this is evident in the organization of the configuration files. See [this page](Projects.md) for more information about the core/project distinction.

## Configuration Files ##

Configuration files are read in the following order, with parameter values in later files overriding earlier ones:
  1. tops/core/config.ini: configures the _core_ software,
  1. tops/sdss3/config.ini: modifies some _core_ configuration parameters and configures the SDSS-3 proxies, and
  1. an optional configuration file provided by the user and [specified on the command line](Running.md).

Here is an excerpt from the SDSS-3 configuration file, tops/sdss3/config.ini:
```
[tcc.listener]
service = tops.sdss3.tcc.listener
launch_order = 120
enable = True
udp_port = 1200
timeout = 5 ; seconds

[tcc.session]
service = tops.sdss3.tcc.session
launch_order = 130
enable = True
telnet_host = tcc25m.apo.nmsu.edu ; will only work on the 2.5m subnet at APO
telnet_port = 23
telnet_user = tcc
telnet_pw = 5d45993fb679c37d25e4753104ff16c7 ; encrypted
```
Note that the file is divided into named sections (tcc.listener and tcc.session in this example) and each section specifies the values of named parameters. Comments begin with a semicolon. The order of sections within an INI file is not important and neither is the order of parameters within a section (unless a parameter is repeated within the same file and section which should not be the case).

## Configuration Parameter Reference ##

A named section with a _service_ parameter identifies a process that can be started to provide a runtime service. The value of the _service_ parameter is the python module path of the service main entry point. The [start program](Running.md) scans through the configuration files to determine the available services and will start them in increasing order of their _launch\_order_ parameter. Use the _enable_ parameter to prevent a service being started.

The following values are considered _True_ / _False_ for boolean parameters (case is ignored):
  * 1 / 0
  * yes / no
  * true / false
  * on / off
All other values will generate a run-time error.

Private data, such as passwords, can be stored with modest security in a configuration file. All private data for a project is encrypted using a master pass phrase that the user must enter when starting the operations software. Private data is then decrypted in memory and distributed via unix pipes to other processes. Although this is much better than storing plain text passwords in a file, it is not an invulnerable solution.

### Core Services ###

The core logging and archiving servers use file-based logging output. The _logfile_ parameter of the _logger_ and _archiver_ sections determines where this output will be stored. Use the special value _stdout_ to print all logging output directly to the shell. Logfiles are automatically rotated when they exceed 1Mbyte in size. In case _logfile_ refers to a non-existent directory, the necessary path will be created automatically.

The following parameters are also shared between the logging and archiving core services:
  * _unix\_addr_: UNIX socket address that the server will listen and local clients will connect to. The corresponding filesystem path will be created if necessary.
  * _tcp\_port_: TCP port number that the server will listen to and remote clients will connect to.
  * _tcp\_host_: TCP host name that remote clients will connect to.
  * _http\_port_: TCP port that the service's web server will listen to.
  * _web\_title_: Ttitle of this service's monitoring web page.

### SDSS-3 Services ###