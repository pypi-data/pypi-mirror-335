import unittest
import numpy as np
from astropy.time import Time
from datetime import datetime, timedelta
from sktimeutils.juliandate import ut_to_jd
from sktimeutils.eci import eciteme_to_itrf, itrf_to_eciteme, gmst, polar_motion_rotation_matrix


# ------------------------------------------------------------------------------
#           Class TestECIConversionFunctions
# ------------------------------------------------------------------------------
class TestECIConversionFunctions(unittest.TestCase):

    def setUp(self):
        self.eciv = np.array([0.8, 2.1, 1.45])
        self.ut = datetime(2009, 11, 15, hour=14, minute=36, second=12, microsecond=123456)
        self.utarray = [self.ut]
        self.ecivarray = [[-2392.11241452386, -17078.1233608647, 19945.4195944851]]
        dt = timedelta(hours=1.0)
        dv = [0.25, 0.23, 0.17]
        v = self.ecivarray[0]
        t = self.ut
        for i in range(24):
            t = t + dt
            self.utarray.append(t)
            v[0] += dv[0]
            v[1] += dv[1]
            v[2] += dv[2]
            self.ecivarray.append(v)
        self.ecivarray = np.array(self.ecivarray).transpose()

    # ------------------------------------------------------------------------------
    #           test_eci_to_geo
    # ------------------------------------------------------------------------------
    def test_eci_to_geo_multi_vector_single_time(self):

        geov = eciteme_to_itrf(self.ecivarray, self.ut)
        neweci = itrf_to_eciteme(geov, self.ut)
        with np.nditer([self.ecivarray, neweci]) as it:  # create the numpy iterator object
            for a, b in it:  # and convert each elemnet
                self.assertAlmostEqual((a.item() - b.item()) / a.item(), 0.0, 6)

    # ------------------------------------------------------------------------------
    #           test_eci_to_geo_multi_vector_multi_time
    # ------------------------------------------------------------------------------
    def test_eci_to_geo_multi_vector_multi_time(self):                          # test N 3 element vectors and N times

        geov = eciteme_to_itrf(self.ecivarray, self.utarray)                  # convert to GEO
        neweci = itrf_to_eciteme(geov, self.utarray)                            # then convert back to ECI
        with np.nditer([self.ecivarray, neweci]) as it:                         # create the numpy iterator object
            for a, b in it:                                                     # and ensure each element has come back to its original value
                self.assertAlmostEqual((a.item() - b.item()) / a.item(), 0.0, 6)

    # ------------------------------------------------------------------------------
    #           test_eci_to_geo_single_vector_single_time
    # ------------------------------------------------------------------------------
    def test_eci_to_geo_single_vector_single_time(self):                            # Test one 3 element vector and one time

        geov = eciteme_to_itrf(self.eciv, self.ut)                                       # Convert to GEO
        neweci = itrf_to_eciteme(geov, self.ut)                                          # then convert back
        with np.nditer([self.eciv, neweci]) as it:                                  # and ensure each element
            for a, b in it:                                                         # has come back to its original value
                self.assertAlmostEqual((a.item() - b.item()) / a.item(), 0.0, 6)

    # ------------------------------------------------------------------------------
    #           test_eci_with_skyfield_values
    # ------------------------------------------------------------------------------
    def test_eci_with_skyfield_values(self):                                                            # Tests ECI to ITRF and vice-versa. Also tests multiple values in one call

        t = Time("2006-07-21 13:30:45.000000", scale='utc')
        st = gmst(t, model='IAU1982')
        self.assertAlmostEqual(st, 2.476013901552527, 8)                                              # This is verified against skyfield to 11 decimal places for IAU 1982
        ecipos = np.array((-2392.11241452386, -17078.1233608647, 19945.4195944851))
        geoans = np.array((-8664.437725340678, 14910.097768385942, 19945.444732408647))        # These are the values which agree with skyfield
        ecivals = np.array((ecipos, ecipos, ecipos, ecipos)).transpose()                       # Make an array of values and reshape so its (3,N) and NOT (N,3)
        itrfvals = eciteme_to_itrf(ecivals, (t, t, t, t), do_polar_motion=True)                  # Convert the ECI to ITRF/GEO
        newecivals = itrf_to_eciteme(itrfvals, (t, t, t, t), do_polar_motion=True)                  # Convert the ITRF back to ECI. should be identical to numerical precision
        for i in range(4):
            for j in range(3):
                self.assertAlmostEqual(itrfvals[j, i], geoans[j], 4)
                self.assertAlmostEqual(newecivals[j, i], ecipos[j], 4)

    # ------------------------------------------------------------------------------
    #           test_julian_date_result
    # ------------------------------------------------------------------------------
    def test_scalar_julian_date_result(self):
        ut = '2011-11-15T19:24:49.000000'
        jd1, jd2 = ut_to_jd(ut)
        self.assertEqual(jd1, 2455881.0)
        self.assertAlmostEqual(jd2, 0.30890046, 7)

    # ------------------------------------------------------------------------------
    #           test_array_julian_date_result
    # ------------------------------------------------------------------------------
    def test_array_julian_date_result(self):
        ut = np.array(['2011-11-15T19:24:49.000000', '2011-11-15T19:24:49.000000', '2011-11-15T19:24:49.000000'], dtype='datetime64')
        jd1, jd2 = ut_to_jd(ut)
        for i in range(3):
            self.assertEqual(jd1[i], 2455881.0)
            self.assertAlmostEqual(jd2[i], 0.30890046, 7)

    # ------------------------------------------------------------------------------
    #           test_gmst_result
    # ------------------------------------------------------------------------------
    def test_gmst_result(self):
        utc = ['1999-01-01T00:01:04.307000', '2010-01-01T00:01:06.184000']
        hourangle = gmst(utc) * 12.0 / np.pi

        self.assertAlmostEqual(hourangle[0], 6.698545632551297, 7)
        self.assertAlmostEqual(hourangle[1], 6.720974822059431, 7)


if __name__ == '__main__':
    unittest.main()
