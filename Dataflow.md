# Types of Operations Data #

The operations software infrastructure divides the data flowing through the system into two broad categories:
  * Logging data is text based and handled by the [logging service](Logging.md).
  * Archiving data is numeric and handled by the [archiving service](Archiving.md).
This distinction is somewhat arbitrary since, for example, logging data is tagged with numeric metadata and text enumerations ("Red","Yellow","Green") are considered numeric. However, it has proven useful and leads to a natural specialization of the services provided for each type.

Logging data consists of a text message that is augmented by a source name and severity code (DEBUG, INFO, WARNING, ERROR, CRITICAL). The text can include any unicode characters that can be encoded into ASCII via UTF-8. From a user's point of view, logging data can be searched for substrings or regular expressions and filtered based on its origin (source name) and severity.

Archiving data is organized into named records, where each record has a UTC time stamp and a list of one or more numerical channels values. Values can be integer or floating point. Automatic mapping of string enumerations to integers is also provided. From a user's point of view, a record collects together a set of channels whose values are always read and written as a group, and thus share a single time stamp.

All operations data is eventually stored permanently in a time-index database. Archiving data can be optionally filtered before it is written, to reduce the storage requirements and minimize noise.

All operations data is tagged with a name describing its origin and these names are organized into a coherent global name space. For example, log messages from the TCC interpreter session proxy are tagged with _tcc.session_ and the archiving channels associated with the TCC UDP broadcasts have names like _tcc.listener.broadcast.bore.x.pos_ and _tcc.listener.broadcast.bore.x.vel_.

One asymmetry in the operations data flow is that the archiving service generates logging data but not vice versa.