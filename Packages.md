# Software Packages #

The operations code is organized into the following hierarchy of packages:
  * tops: Telesope Operations Software
    * core: Core services
      * design: Supports the design phase of a project
      * network: Core networking code
        * archiving: Archiving support code
        * logging: Logging support code
        * web: static web content served by the archiving and logging clients
      * protobuf: Google protocol buffer specifications
      * utility: common utilities
    * sdss3: SDSS-3 project-specific services
      * design: Design documents for the SDSS-3 operations software
        * web: support files for automatically-generated design documents
        * iop: Tools for automated analysis of the legacy IOP tcl code
      * tcc: Supports the two TCC proxies
      * marvels: Supports the MARVELS proxy
The top-level division between _core_ and _sdss3_ is [explained here](Projects.md).