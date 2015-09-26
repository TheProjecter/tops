# Telescope Control Computer #

The TCC is an OpenVMS system located in the APO computer room that talks directly to the devices that control and monitor the telescope. The TCC neatly hides most of the details of these devices and is effectively the only device that the operations software needs to interface with. Extensive documentation on the TCC is [available here](http://www.apo.nmsu.edu/Telescopes/TCC/index.html).

The TCC communicates in two ways:
  1. via periodic (1 Hz) UDP broadcasts on its local subnet, and
  1. via an interactive command interpreter.
The operations software provides two proxies for interfacing with the telescope, one for each mode of communication.

## UDP Proxy ##

The proxy that listens to the TCC's periodic UDP broadcasts is named `tcc.listener` and monitors a single timestamped archiving record `tcc.listener.broadcast` with the following channels that directly correspond to the [fields documented here](http://www.apo.nmsu.edu/Telescopes/TCC/UDPPackets.html):

| **Name** | **Type** |
|:---------|:---------|
| slewEndTime |	double   |
| obj.coordSys | 'ICRS','FK5','FK4','Gal','Geo','None','Topo','Obs','Phys','Mount','Inst','GImage' |
| epoch    |	double   |
| obj.axis1.pos |	double   |
| obj.axis1.vel |	double   |
| obj.axis2.pos |	double   |
| obj.axis2.vel |	double   |
| bore.x.pos |	double   |
| bore.x.vel |		double  |
| bore.y.pos |		double  |
| bore.y.vel |	double   |
| rot.type | 'None','Obj','Horiz','Phys','Mount' |
| rot.pos  |		double  |
| rot.vel  |		double  |
| obj.ang.pos |		double  |
| obj.ang.vel |	double   |
| spider.ang.pos |	double   |
| spider.ang.vel |	double   |
| tcc.az.pos |	double   |
| tcc.az.vel |	double   |
| tcc.alt.pos |		double  |
| tcc.alt.vel |	double   |
| tcc.rot.pos |		double  |
| tcc.rot.vel |	double   |
| tcc.sec.focus |	double   |

All of the channel names above are embedded in the global namespace with the prefix `tcc.listener.broadcast.` The dot-notation hierarchy in the channel names allows logical groups of channels to be easily selected with text patterns such as `tcc.listener.broadcast.bore.*` or `tcc.*.vel`.

The `broadcast` record's timestamp is derived from the UDP packet's TAIDate field but is converted to UTC (adjusting for leap seconds).

## Interpreter Proxy ##

The proxy that communicates with the TCC via its interactive command interpreter is named `tcc.session` and monitors a timestamped archiving record for each of the TCC message keywords [described here](http://www.apo.nmsu.edu/Telescopes/TCC/MessageKeywords.html). Unlike the listener proxy, the session proxy can also be controlled via most of the 20 commands [described here](http://www.apo.nmsu.edu/Telescopes/TCC/Commands.html) (some are not relevant for SDSS-3, such as those that communicate with the guider).

From the TCC's point of view, the operations software is logged in as an interactive user. Since the TCC does not support secure-shell logins, the software connects via the less secure telnet (the mechanism for providing the necessary password is [described here](RuntimeConfig.md)).

The `tcc.session` proxy is implemented as a pair of telnet sessions that both login to the TCC when the proxy is started. One session remains at the VMS DCL prompt and the other launches the TCC's interactive interpreter program. Both sessions provide a queue that commands can be added to asynchronously: for the VMS session these are DCL commands while for the interpreter session these are TCC commands. Each session runs a state machine that monitors the output to determine when a command has completed and the next queued command, if any, can be issued. The original issuer of a command is notified (via the the [Twisted](TechnologyChoices.md) deferred mechanism) when the command has completed.

In this way, the proxy serves as a TCC hub, providing a single point of access to the TCC interpreter and allowing safe access patterns to be enforced. Of course, this assumes that no other interpreter sessions are active. Other interpreter users can be monitored and, if necessary, disconnected via the TCC proxy but an appropriate policy for doing this still needs to be established.