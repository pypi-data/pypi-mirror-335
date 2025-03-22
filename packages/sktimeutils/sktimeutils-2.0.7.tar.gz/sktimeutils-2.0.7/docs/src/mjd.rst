..  _mjd_api:

*********************************
UT Conversion. Arrays and Scalars
*********************************

This is a description of the **sktimeutils.mjd** module. It provides several utility
functions to convert to and from modified julian date. The example below demonstrates how to convert 
standard python representations of UTC into mjd::


    import numpy as np
    from datetime import datetime
    from sktimeutils.mjd import ut_to_mjd

    tstr        = '2019-01-11 15:32:45.123456'
    tdatetime   = datetime.fromisoformat( tstr)
    tdatetime64 = np.datetime64(tstr,dtype='datetime64[ms]')

    mjda = ut_to_mjd( tstr )            # Test scalar UTC string to julian date
    mjdb = ut_to_mjd( tdatetime )       # Test scalar datetime to julian date
    mjdc = ut_to_mjd( tdatetime64 )     # Test scalar numpy.datetime64 to julian date

    print( 'mjd from str        = ', jda)
    print( 'mjd from datetime   = ', jdb)
    print( 'mjd from datetime64 = ', jdc)

The `ut_to_mjd` function also supports arrays or lists of time objects/strings and generates arrays of jd1 and jd2. For example, using strings::

    import numpy as np
    from datetime import datetime
    from sktimeutils.juliandate import ut_to_mjd

    tstr  = ['2019-01-11 15:32:45.123456', 2019-01-12 16:32:45.123456', 2019-01-13 17:32:45.123456']
    mjd   = ut_to_mjd( tstr )                            # Test array UTC string to modified julian date

    print( 'First  mjd  = ', mjd[0])
    print( 'Second mjd  = ', mjd[1])
    print( 'Third  mjd  = ', mjd[2])


ut_to_mjd
---------
.. autofunction:: sktimeutils.ut_to_mjd

mjd_to_ut
---------
.. autofunction:: sktimeutils.mjd.mjd_to_ut

ut_to_datetime
--------------
.. autofunction:: sktimeutils.ut_to_datetime

ut_to_datetime64
----------------
.. autofunction:: sktimeutils.ut_to_datetime64

datetime64_to_timestamp
-----------------------
.. autofunction:: sktimeutils.datetime64_to_timestamp

ut_to_jd
--------
.. autofunction:: sktimeutils.ut_to_jd

utc_to_astropy
--------------
.. autofunction:: sktimeutils.utc_to_astropy

**********************
UT Conversion. Scalars
**********************

mjd_to_datetime
---------------
.. autofunction:: sktimeutils.mjd.mjd_to_datetime

mjd_to_datetime64
-----------------
.. autofunction:: sktimeutils.mjd.mjd_to_datetime64

datetime64_to_datetime
----------------------
.. autofunction:: sktimeutils.datetime64_to_datetime
