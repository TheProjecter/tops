# Proxies #

A _proxy_ is a software process that interfaces a specific device (usually a piece of hardware) to the other processes that make up the operations system. Together, the proxies provide a layer that interfaces the physical operations environment to the [operations applications](Applications.md). The reason that such an interface layer is needed is that each device is different, with its own interfaces (serial port, telnet, socket, ...) and protocols, and operates more or less independently of other devices, while applications are best developed and deployed in a more uniform and controlled environment.

In more practical terms, a proxy is a single unix process running a python program that communicates with the operations infrastructure (logging, archiving, etc) via standard protocols over network sockets. It also communicates with whatever device it wraps using whatever interfaces and protocols are necessary. All of the asynchronous communications required are handled via the Twisted Matrix library (more [details here](TechnologyChoices.md).)

From an application's point of view, a proxy provides the following services on behalf of the device it wraps:
  * Health: monitors whether the device is alive and communicating.
  * Channels: reads and, optionally, writes keyword-value pairs.
  * States: models the operating modes of the device with a simple state machine and allows the current state to be monitored and, optionally, changed.
There are two operations that allow an application to control a device:
  * writing a new value to a channel, and
  * triggering a change of state.
These are conceptually different since one has an associated value but generally does not change the device's state, while the other is primarily a control and timing signal. If it helps, think of these as being analogous to the data bus and interrupt/strobe lines of a computer, respectively.

The data flowing out of a device through its proxy is channeled to the [logging](Logging.md) and [archiving](Archiving.md) services. The difference between these is [explained here](Dataflow.md).