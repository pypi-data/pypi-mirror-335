import unittest
import numpy as np
from datetime import datetime
from sktimeutils import ut_to_mjd, ut_to_datetime64


class TestMjdConversions(unittest.TestCase):

    def test_mjdconversion(self):
        tstr = '2019-01-11 15:32:45.123456'
        t1 = datetime.fromisoformat(tstr)
        t2 = np.datetime64(tstr, 'ms')

        mjd1 = ut_to_mjd(t1)                                # Test scalar datetime to mjd
        mjd2 = ut_to_mjd(mjd1)                              # Test scalar float to mjd
        mjd3 = ut_to_mjd(tstr)                              # Test scalar string to mjd
        mjd4 = ut_to_mjd(t2)                                # Test scalar datetime64 to mjd

        mjd10 = ut_to_mjd([t1, t1, t1])                     # Test list of datetime
        mjd20 = ut_to_mjd([mjd1, mjd1, mjd1])               # Test list of scalar
        mjd30 = ut_to_mjd([tstr, tstr, tstr])               # Test list of string
        mjd40 = ut_to_mjd([t2, t2, t2])                     # Test list of datetime64

        self.assertAlmostEqual(mjd1, 58494.64774448444, 7)
        self.assertAlmostEqual(mjd2, 58494.64774448444, 7)
        self.assertAlmostEqual(mjd3, 58494.64774448444, 7)
        self.assertAlmostEqual(mjd4, 58494.64774448444, 7)
        for i in range(3):
            self.assertAlmostEqual(mjd10[i], 58494.64774448444, 7)
            self.assertAlmostEqual(mjd20[i], 58494.64774448444, 7)
            self.assertAlmostEqual(mjd30[i], 58494.64774448444, 7)
            self.assertAlmostEqual(mjd40[i], 58494.64774448444, 7)

    def test_datetime64conversion(self):
        tstr = '2019-01-11 15:32:45.123456'
        t1 = datetime.fromisoformat(tstr)
        t2 = np.datetime64(tstr, 'ms')

        mjd1 = ut_to_mjd(ut_to_datetime64(t1))                            # Test scalar datetime to mjd
        mjd2 = ut_to_mjd(ut_to_datetime64(mjd1))                           # Test scalar float to mjd
        mjd3 = ut_to_mjd(ut_to_datetime64(tstr))                          # Test scalar string to mjd
        mjd4 = ut_to_mjd(ut_to_datetime64(t2))                             # Test scalar datetime64 to mjd

        mjd10 = ut_to_mjd(ut_to_datetime64([t1, t1, t1]))                    # Test list of datetime
        mjd20 = ut_to_mjd(ut_to_datetime64([mjd1, mjd1, mjd1]))              # Test list of scalar
        mjd30 = ut_to_mjd(ut_to_datetime64([tstr, tstr, tstr]))              # Test list of string
        mjd40 = ut_to_mjd(ut_to_datetime64([t2, t2, t2]))                    # Test list of datetime64

        self.assertAlmostEqual(mjd1, 58494.64774448444, 7)
        self.assertAlmostEqual(mjd2, 58494.64774448444, 7)
        self.assertAlmostEqual(mjd3, 58494.64774448444, 7)
        self.assertAlmostEqual(mjd4, 58494.64774448444, 7)
        for i in range(3):
            self.assertAlmostEqual(mjd10[i], 58494.64774448444, 7)
            self.assertAlmostEqual(mjd20[i], 58494.64774448444, 7)
            self.assertAlmostEqual(mjd30[i], 58494.64774448444, 7)
            self.assertAlmostEqual(mjd40[i], 58494.64774448444, 7)


if __name__ == '__main__':
    unittest.main()
