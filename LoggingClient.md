## Logging Client ##

The [logging service](Logging.md) provides a central hub that all the [text-based data](Dataflow.md) produced by the operations software flows through and is then stored permanently.

The logging client provides a web interface to the transient logging data flowing through the system right now (or recently). A similar client will eventually provide access to historical logging data from the persistent database.

The only requirement for running the logging client is a reasonably modern browser (tested platforms are [listed here](Platforms.md)). The exact URL will depend on the [run-time configuration](RuntimeConfig.md) and on which host the logging process is running on, but will be something like:

http://sdssfiles1.apo.nmsu.edu:8080/local/logwatch.html

The number 8080 is required since the software uses a non-standard port for http, which avoids any conflicts with a production web server running on the standard port 80 and also allows other operations software services to run their own servers on different ports.

The screenshots below show the logging client in action. In the first, log messages are being displayed. Color codes indicate the message severity and the message source appears on the left. The second screenshot shows the configuration dialog for source and severity filtering, etc.

![http://tops.googlecode.com/svn/wiki/images/LoggingClient1.png](http://tops.googlecode.com/svn/wiki/images/LoggingClient1.png)

![http://tops.googlecode.com/svn/wiki/images/LoggingClient2.png](http://tops.googlecode.com/svn/wiki/images/LoggingClient2.png)

Note that the logging service generates its own periodic 'heartbeat' messages (with a severity level of _DEBUG_) so you know it is still alive and that you have not been missing messages.
```
Server has been running 0:01:00 and handled 15 messages.
```
The **Last Update..** and **Showing...** messages on the lower status line are also useful for monitoring the logging service.