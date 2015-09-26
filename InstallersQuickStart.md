# Quick Start Guide for Software Installers #

This page collects together useful links for installing the operations software. There are similar guides for software [users](UsersQuickStart.md) and [developers](DevelopersQuickStart.md).

## Preparing to Install ##

This software is written mostly in python (there is also some javascript that only web clients run) and so should be widely portable. The code has been tested on the [following platforms](Platforms.md).

  1. Check if your platform has the [required software environment](RequiredEnvironment.md) and upgrade or install packages if necessary.
  1. Decide which [software release](ReleaseNotes.md) you will install.
  1. Obtain a [copy of the software](Downloading.md).

## Building the Software ##

There is nothing that requires compiling or linking in the software but some files are deliberately not stored in the code repository since they can be generated from other files already in the repository. The steps required to reconstruct these files are coordinated by the [required](RequiredEnvironment.md) SConstruct build program.

  1. Build the python descriptions of the [protocol buffers](TechnologyChoices.md) (this step is **required**).
  1. Build the web pages that document the design (this step is optional).
  1. Build the [source code documentation](CodeDocs.md) web pages (this step is optional).

## Testing your Installation ##

  1. Running [automatic unit tests](UnitTests.md).
  1. Running [non-automated tests](OtherTests.md).
  1. [Running the operations software](Running.md).