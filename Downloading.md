# Downloading the Operations Software #

**As of 6 Oct 2008, active development of the code repository has moved to [sdss3.org](http://trac.sdss3.org/wiki/TOPS/Downloading)**.

## Tagged Releases ##

You can get a list of all the available tagged releases with:
```
% svn list --verbose http://tops.googlecode.com/svn/tags
```
To check out a read-only copy of a tagged version use, for example (checks out V0.1):
```
% svn checkout http://tops.googlecode.com/svn/tags/V0.1 tops
```
This will create and fill a tops/ subdirectory of your current working directory.

In the future, tagged releases may also be available as downloadable archives (tar.gz or zip) from the [project's download page](http://code.google.com/p/tops/downloads/list). Is there a need for this?

## Development Snapshot ##

To install the most recent development snapshot, use:
```
% svn checkout http://tops.googlecode.com/svn/trunk tops
```
This will create and fill a tops/ subdirectory of your current working directory. You can update your snapshot at any time (assuming you have not changed it) using, from the same working directory:
```
% svn update tops
```