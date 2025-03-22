..  _eci_api:


ECI & Sidereal Time
===================

This is a description of the **sktimeutils.eci** module. This module sprovides the capability to convert from Earth
Centered Inertial, **ECI**, to geocentric coordinates, **GEO**. The **ECI** coordinates are assumed to be specified with
the true equator and mean equinox. The conversion from ECI to GEO is a rotation around the Z axis based upon the
Greenwich Mean Sidereal Time, see function **gmst**.

eciteme_to_itrf
---------------

.. autofunction:: sktimeutils.eci.eciteme_to_itrf

itrf_to_eciteme
---------------

.. autofunction:: sktimeutils.eci.itrf_to_eciteme


gmst
----

.. autofunction:: sktimeutils.eci.gmst


polar_motion_rotation_matrix
-----------------------------


.. autofunction:: sktimeutils.eci.polar_motion_rotation_matrix

