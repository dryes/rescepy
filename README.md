rescepy
=====

a cross-platform python2 script for automated srr (rescene) verification and reconstruction.

* fetches srrs from: http://www.srrdb.com
* verifies sfv files and reconstructs rars and samples if required.
* ability to identify and process extracted files (video only).


## dependencies:

* [Python2][python]
* [pyReScene][pyrescene]
* [UnRAR][unrar]
* [cfv][cfv]


## usage:

* python2 resce.py [--opts] input1 [input2] ...

* windows guide: http://rescene.wikidot.com/rescepy

## notes:

* for reconstruction of compressed rars it is required that you have run preprardir.py included with pyrescene -- also see --rar-dir option.
* running Goober's awescript with: '--no-srr --no-srs' is recommended before processing with rescepy.
* releases determined to be fixes (eg. DiRFiX, SUBFiX, etc.) are skipped to avoid problems.
* pyrescene must be installed (with setup.py) to allow for the importing of its modules.
* windows users: ensure all dependencies are included in your PATH.

* had to fork this due to losing access to my original github and email accounts over a year ago.

[python]: http://www.python.org/
[pyrescene]: https://bitbucket.org/Gfy/pyrescene
[unrar]: http://www.rarlab.com/
[cfv]: http://cfv.sourceforge.net/
