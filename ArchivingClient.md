# Archiving Client #

The [archiving service](Archiving.md) provides a central hub that all the [numeric data](Dataflow.md) produced by the operations software flows through and is then stored permanently.

The archiving client provides a web interface to the transient archiving data flowing through the system right now (or recently). A similar client will eventually provide access to historical archiving data from the persistent database.

The only requirement for running the archiving client is a reasonably modern browser (tested platforms are [listed here](Platforms.md)). The exact URL will depend on the [run-time configuration](RuntimeConfig.md) and on which host the logging process is running on, but will be something like:

http://sdssfiles1.apo.nmsu.edu:8081/local/archiver.html

The number 8081 is required since the software uses a non-standard port for http, which avoids any conflicts with a production web server running on the standard port 80 and also allows other operations software services to run their own servers on different ports.

The screenshots below show the archiving client in action. The first shows the initial view where you are prompted to enter a wildcard pattern for the channels you wish to monitor. The second shows a series of channels being displayed, with their values updated in real time. At any time, the user can enter a new wildcard pattern to display a different set of channels. Channels can be re-ordered by dragging them within the web page.

![http://tops.googlecode.com/svn/wiki/images/ArchivingClient1.png](http://tops.googlecode.com/svn/wiki/images/ArchivingClient1.png)

![http://tops.googlecode.com/svn/wiki/images/ArchivingClient2.png](http://tops.googlecode.com/svn/wiki/images/ArchivingClient2.png)

The current implementation of the archiving client is fairly minimal but demonstrates the potential. A second client that displays strip charts of arbitrary channels versus time will be an essential tool for system's debugging and monitoring trends. For more information about what this might look like, refer to the [EPICS strip tool documentation](http://www.aps.anl.gov/epics/extensions/StripTool/index.php).