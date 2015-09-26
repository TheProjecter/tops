# Notes for the 25 Sep 2008 SDSS-3 Infrastructure Meeting #

After a productive week of commissioning at APO, an initial [infrastructure release](ReleaseNotes.md) of the new operations software is now available. The software now also has a name, TOPS, for Telescope OPerations Software.

The software is being developed as an [open source project](License.md) hosted at http://tops.googlecode.com, which includes a public code repository, a documentation wiki (which you are reading now), and issue tracker.

The following wiki pages provide a quick overview of the project and its current status as input for today's discussion:
  * [An overview of the design](DesignOverview.md).
    * [What is a proxy](Proxies.md)?
    * [The difference between logging and archiving](Dataflow.md).
  * [TUI, TRON and all that](TechnologyChoices.md).
  * [What is the current status](ReleaseNotes.md)?
    * [Configuring the operations software](RuntimeConfig.md).
    * [Starting the operations software](Running.md).
    * [Interface to the TCC](TCC.md).
    * [Using the logging client](LoggingClient.md).
    * [Using the archiving client](ArchivingClient.md).
    * [Plans for MARVELS](MARVELS.md).
    * The code is [documented](CodeDocs.md).
    * The code is [tested](UnitTests.md).
For more details, select one of the following guides aimed at different audiences:
  * [User's quick-start guide](UsersQuickStart.md).
  * [Installer's quick-start guide](InstallersQuickStart.md).
  * [Developer's quick-start guide](DevelopersQuickStart.md).