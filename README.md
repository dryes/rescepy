rescepy
=====

rescepy is a cross-platform Python script for automated ReScene reconstruction.

* Zero user intervention required - entirely automated.
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
* By default the srr is saved inside the release directory - this can be changed with the '--srr-dir' option.


## notes:

* If rars exist without passing '-f' (force), the directory structure may be disrupted.
*   - run Goober's Awescript with: '--no-srr --no-srs' to remedy this.
* *nix users: it is assumed that you have created scripts in /usr/bin/ to call: mono /path/to/srr.exe
* Windows users: ensure all dependencies are included in your PATH.
* Releases determined to be fixes (eg. DiRFiX, SUBFiX, etc.) or non-video are skipped.

[python]: http://www.python.org/
[rescene]: http://www.srrdb.com/software.php
[resample]: http://www.srrdb.com/software.php
[unrar]: http://www.rarlab.com/
[cfv]: http://cfv.sourceforge.net/
