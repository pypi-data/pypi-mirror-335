###########
sktimeutils
###########
Package ``sktimeutils`` provides a suite of utility functions for manipulating time. Its primary purpose is to convert objects
from one time format to another. The package supports the following time formats

#. ``datetime``. The builtin datetime object supplied with python.
#. ``numpy.datetime64``. The builtin datetime object used by ``numpy``. This is often used in arrays of time
#. ``str``. Strings are often convenient to represent time. We assume all times represent Universal Time and support strings endoded in the isoformat
#. ``float``. We assume floats are modified julian date (mjd)

The package provides functions that converts one time format to another, but perhaps more usefully, it provides functions
that convert arrays of time values, which are expressed in any one of the above formats, to arrays of time expressed in
the desired format.

The package also provides functions to convert from ECI/TEME coordinates to ECEF/ITRF coordinate as this is intimately
linked with sidereal time calculations.

.. toctree::
   :maxdepth: 2

   installation
   mjd
   juliandate
   eci


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
