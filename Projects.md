# Core and Project Software #

The operations software is organized with a clean dividing line between _core_ code and _project_ code. In practice, the software is being developed with only one project in mind, SDSS-3, but making this distinction leads to a cleaner and more extensible design.

By definition, the _core_ code provides the infrastructure services that any project would need: logging, archiving, process control, etc. It also defines the common behavior of all proxies.

_Project_ code, on the other hand, is specific to a particular project and so includes the actual implementations of the project's proxies, for example.

In practical terms, the core/project distinction refers to a top-level branch in the python package hierarchy: core code lives under tops.core and SDSS-3 code lives under tops.sdss3.

The core/project leads to some interesting design challenges such as how to start the operations software, which is a core service, without knowing what project-specific proxies are required. In general, bootstrap problems like this can be elegantly solved with a combination of command-line parameters and [run-time configuration](RuntimeConfig.md). See [here for details](Running.md).