# Other Tests #

Some of the testing code in the operations software can not be easily packaged as an [automatic unit test](UnitTests.md).

## Telnet Session Test ##

The core networking code includes a test of the telnet session infrastructure. It creates two telnet client sessions, both to localhost, that run in parallel handling asynchronous commands. One session allows command to
be sent directly to the login shell and the other runs ftp and interfaces to the ftp command line.

The code includes connection parameters that will generally need to be customized for the testing host. Tthe telnet service must be also enabled on localhost (which is a security risk and so should not be enabled permanently).

Here is an example of successfully running telnet\_test (not that the system's telnet service is enabled just for this test and then disabled afterwards):
```
% sudo /sbin/service telnet start
% python tops/core/network/telnet_test.py
Enter password for david@localhost: 
Running ftp_commands...
the answer to "debug toggle 1" is:
debug
Debugging on (debug=1).
the answer to "help set" is:
help set
set        	set or display options
the answer to "debug toggle 2" is:
debug
Debugging off (debug=0).
Running localhost_commands...
the answer to "pwd" is:
/Users/david
the answer to "whoami" is:
david
% sudo /sbin/service telnet stop
```