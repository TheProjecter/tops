# Automatic Unit Tests #

Non-automated tests are [described here](OtherTests.md).

The operations software makes extensive use of unit tests embedded within python modules that can be automatically extracted and run. The top-level program run\_tests.py finds the available tests and runs them:
```
% python tops/run_tests.py
## Running run_tests.py on Wed Sep 24 16:04:34 2008
2.5.2 (r252:60911, Feb 22 2008, 07:57:53) 
[GCC 4.0.1 (Apple Computer, Inc. build 5363)]

## Scanning for tests in the module tree of "tops" from /Users/david/Cosmo/SDSS/Design/dev/tops
tops
  tops.start                               ...   0 test case(s)
tops.core
tops.core.design
  tops.core.design.domain_model            ...   7 test case(s)
  tops.core.design.use_cases               ...   0 test case(s)
tops.core.network
  tops.core.network.client                 ...   0 test case(s)
  tops.core.network.client_server_test     ...   3 test case(s)
  tops.core.network.command                ...   7 test case(s)
  tops.core.network.naming                 ...   5 test case(s)
  tops.core.network.proxy                  ...  23 test case(s)
  tops.core.network.server                 ...   0 test case(s)
  tops.core.network.telnet                 ...   0 test case(s)
  tops.core.network.telnet_test            ...   0 test case(s)
  tops.core.network.webserver              ...   0 test case(s)
tops.core.network.archiving
  tops.core.network.archiving.producer     ...   0 test case(s)
  tops.core.network.archiving.record       ...   1 test case(s)
  tops.core.network.archiving.server       ...   0 test case(s)
tops.core.network.logging
  tops.core.network.logging.producer       ...   0 test case(s)
  tops.core.network.logging.record         ...   0 test case(s)
  tops.core.network.logging.server         ...   0 test case(s)
  tops.core.network.logging.test           ...   0 test case(s)
tops.core.utility
  tops.core.utility.astro_time             ...   7 test case(s)
  tops.core.utility.config                 ...   0 test case(s)
  tops.core.utility.data                   ...   9 test case(s)
  tops.core.utility.html                   ...   4 test case(s)
  tops.core.utility.name_graph             ...  16 test case(s)
  tops.core.utility.options                ...   0 test case(s)
  tops.core.utility.secret                 ...  11 test case(s)
  tops.core.utility.state_chart            ...  23 test case(s)
tops.sdss3
tops.sdss3.design
  tops.sdss3.design.general_cases          ...   0 test case(s)
  tops.sdss3.design.marvels_cases          ...   0 test case(s)
  tops.sdss3.design.marvels_states         ...  23 test case(s)
  tops.sdss3.design.model                  ...   7 test case(s)
  tops.sdss3.design.path                   ...   0 test case(s)
  tops.sdss3.design.tcc_states             ...  23 test case(s)
tops.sdss3.tcc
  tops.sdss3.tcc.broadcast                 ...   0 test case(s)
  tops.sdss3.tcc.listener                  ...  23 test case(s)
  tops.sdss3.tcc.message                   ...   7 test case(s)
  tops.sdss3.tcc.session                   ...  23 test case(s)

## Running tests
...............................................................................................................
...............................................................................................................
----------------------------------------------------------------------
Ran 222 tests in 2.184s

OK
```
This script currently requires that PYTHONPATH be set and include the parent of your top-level tops/ directory. In the future, automated testing will be performed by the SConstruct build tool.

One module, tops/core/network/client\_server\_test, exists only to provide unit tests and is one of the most complex tests since it invokes multiple processes to test the basic client-server handshake over a socket.