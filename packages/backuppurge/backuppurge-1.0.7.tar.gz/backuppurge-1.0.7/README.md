
backuppurge
===========

Selectively purge daily full backups, but keeping some:

* Keep all daily backups for the last X days
* Keep one daily backup per month for the last Y months
* Keep one yearly backup per year for the last Z years
* Keep recent backups for the last R backups

Backup file names must have `YYYY-MM-DD` in their filename somewhere
(in that format) and must have the same prefix/postfix, e.g.:

    homedir_2013-03-31.tgz
    homedir_2013-03-30.tgz
    ...


Documentation
-------------

Usage information can be found in the man page.


Dependencies
------------

* [Python](https://python.org/) 3.5 or newer
* *Optional:* [pytest](https://pytest.org/) for running unit tests
* *Optional:* [docutils](https://docutils.sourceforge.io/) for updating the manpage


Running Tests
-------------

To run the test suite:

    python3 -m pytest -v


Updating the documentation
--------------------------

To convert the README file to a website and to update the manual page:

    python3 update_docs.py


Website
-------

* https://thp.io/2013/backuppurge/
* https://pypi.python.org/pypi/backuppurge/


License
-------

[Simplified BSD License](LICENSE)
