..  _jd_api:


Julian date
===========

Functions have been provided that convert universal time to Julian Date. The code internally utilizes the `jdcal <https://pypi.org/project/jdcal/>`_ package to provide the conversion and provides several functions that wrap the
call. Most users should be content calling `ut_to_jd` which is able to convert scalars, sequences or np.ndarrays of strings, datetime, datetime64, or floats to julian date. Each julian date is returned as two parts, the julian day and the fraction of julian day.
For example::

    import numpy as np
    from datetime import datetime
    from sktimeutils.juliandate import ut_to_jd

    tstr        = '2019-01-11 15:32:45.123456'
    tdatetime   = datetime.fromisoformat( tstr)
    tdatetime64 = np.datetime64(tstr,dtype='datetime64[ms]')

    jda1,jda2 = ut_to_jd( tstr )            # Test scalar UTC string to julian date
    jdb1,jdb2 = ut_to_jd( tdatetime )       # Test scalar datetime to julian date
    jdc1,jdc2 = ut_to_jd( tdatetime64 )     # Test scalar numpy.datetime64 to julian date

    print( 'jd from str        = ', jda1,' + ',jda2 )
    print( 'jd from datetime   = ', jdb1,' + ',jdb2 )
    print( 'jd from datetime64 = ', jdc1,' + ',jdc2 )


The `ut_to_jd` function also supports arrays or lists of time objects/strings and generates arrays of jd1 and jd2. For example, using strings::

    import numpy as np
    from datetime import datetime
    from sktimeutils.juliandate import ut_to_jd

    tstr      = ['2019-01-11 15:32:45.123456', 2019-01-12 16:32:45.123456', 2019-01-13 17:32:45.123456']
    jda1,jda2 = ut_to_jd( tstr )                            # Test array UTC string to julian date

    print( 'First jd   = ', jda1[0],' + ',jda2[0] )
    print( 'Second jd  = ', jda1[1],' + ',jda2[1] )
    print( 'Third jd   = ', jda1[2],' + ',jda2[2] )


datetime_to_jd
--------------

.. autofunction:: sktimeutils.juliandate.datetime_to_jd

datetime64_to_jd
----------------

.. autofunction:: sktimeutils.juliandate.datetime64_to_jd

isoformat_to_jd
---------------

.. autofunction:: sktimeutils.juliandate.isoformat_to_jd

number_to_jd
------------

.. autofunction:: sktimeutils.juliandate.number_to_jd



