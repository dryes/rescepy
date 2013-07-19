rescepy
=====

rescepy is a cross-platform Python script for automated ReScene reconstruction.

* Zero user intervention required - entirely automated.
* Grabs the latest srrs from srrdb.com.
* Option to process samples only.

## dependencies:

* [Python3][python]
* [pyReScene][pyrescene]
* [UnRAR][unrar]
* [cfv][cfv]


## usage:

* Simply download, retaining directory structure, and run resce.py (-h for help).
* By default the srr is saved inside the release directory - this can be changed with the '--srr-dir' option.


## notes:

* It is recommended you run Goober's Awescript with: '--no-srr --no-srs' before processing with rescepy to avoid missing file errors.
* Windows users: ensure all dependencies are included in your PATH.
* Releases determined to be fixes (eg. DiRFiX, SUBFiX, etc.) or non-video are skipped.

[python]: http://www.python.org/
[pyrescene]: https://bitbucket.org/Gfy/pyrescene
[unrar]: http://www.rarlab.com/
[cfv]: http://cfv.sourceforge.net/
