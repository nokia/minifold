Minifold
==============

.. _Python: http://python.org/
.. _git: https://github.com/nokia/minifold.git 

==================
Dependencies
==================

Minifold requires Python_ 3.

To use all connectors, it is advised to also install the following packages:

- `python3-ldap3` for LDAP connector;
- `python3-pycountry` and `python3-urllib3` for HAL and DBLP connectors;
- `python3-tweepy` for Twitter connector.

For example, under Debian-based distribution, run:

```bash
  sudo apt-get update
  sudo apt-get install python3 python3-ldap3 python3-pycountry python3-urllib3 python3-tweepy
```

==================
Installation steps
==================
From sources
------------------

- The sources are available on the minifold git_.

  mkdir ~/git
  git clone https://github.com/nokia/minifold.git
  cd ~/git/minifold
  python3 setup.py build
  sudo python3 setup.py install

==================
Testing
==================

1. Test scripts are provided in tests/ directory.
2. Install `python3-pytest`. 
3. Run tests as follows:

  cd ~/git/minifold/tests/
  pytest-3

==================
Packaging
==================

Install the packages needed to build `.rpm` and `.deb` packages:

- `python3-setuptools`
- `python3-stdeb` for `.deb` packages
- `rpm` for `.rpm` packages

For example, under Debian-based distribution, run:

  sudo apt-get update
  sudo apt-get install python3-setuptools python3-stdeb rpm

To build `.rpm` package (in `dist/`), run:

  cd ~/git/minifold/tests/
  python3 setup.py bdist_rpm

To build `.deb` package (in `deb_dist`), run:

  python3 setup.py --command-packages=stdeb.command bdist_deb

