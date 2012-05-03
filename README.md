rescepy
=====

rescepy is a Python script for automated ReScene reconstruction.

* Cross-platform for the first time.
* Grabs the latest srrs from srrdb.com.
* Option to process samples only.

## dependencies:

* [Python3][python]
* [ReScene][rescene]
* [ReSample][resample]
* [UnRAR][unrar]
* [cfv][cfv]


## usage:

* Simply download, retaining directory structure, and run resce.py (-h for help).
* Default srr storage directory is inside the release dir. - this can be changed with the --srr-dir option.


## notes:

* Use with caution - do not pass in directories that are not intended for processing.

[python]: http://www.python.org/
[rescene]: http://www.srrdb.com/software.php
[resample]: http://www.srrdb.com/software.php
[unrar]: http://www.rarlab.com/
[cfv]: http://cfv.sourceforge.net/
