import unittest
import numpy as np
from datetime import datetime
from sktimeutils import ut_to_mjd, ut_to_datetime, ut_to_datetime64


# ------------------------------------------------------------------------------
#           Class TestECIConversionFunctions
# ------------------------------------------------------------------------------
class TestConversionFunctions(unittest.TestCase):

    def setUp(self):

        self.utobj_array = [datetime(1959, 11, 15, hour=6, minute=20, second=12, microsecond=123456),
                            datetime(2020, 11, 15, hour=15, minute=37, second=12, microsecond=123456),
                            datetime(2059, 11, 15, hour=6, minute=59, second=59, microsecond=999999)]
        self.utstr_array = ['1959-11-15T06:20:12.123456',
                            '2020-11-15T15:37:12.123456',
                            '2059-11-15T06:59:59.999999']
        self.utd64_array = [np.datetime64('1959-11-15T06:20:12.123456'),
                            np.datetime64('2020-11-15T15:37:12.123456'),
                            np.datetime64('2059-11-15T06:59:59.999999')]

        self.utmjd_array = [36887.264029206664,
                            59168.65083476222,
                            73412.29166666666]

    # ------------------------------------------------------------------------------
    #           test_eci_to_geo
    # ------------------------------------------------------------------------------
    def test_ut_to_mjd(self):
        """
        Tests the array and scalar based methods of converting various times to MJD.
        These all should give the same answer.
        """

        t1 = ut_to_mjd(self.utobj_array)
        t2 = ut_to_mjd(self.utstr_array)
        t3 = ut_to_mjd(self.utd64_array)
        t4 = ut_to_mjd(self.utmjd_array)
        s1 = ut_to_mjd(self.utobj_array[0])
        s2 = ut_to_mjd(self.utstr_array[0])
        s3 = ut_to_mjd(self.utd64_array[0])
        s4 = ut_to_mjd(self.utmjd_array[0])
        for i in range(3):
            self.assertAlmostEqual(t1[i], self.utmjd_array[i])
            self.assertAlmostEqual(t2[i], self.utmjd_array[i])
            self.assertAlmostEqual(t3[i], self.utmjd_array[i])
            self.assertAlmostEqual(t4[i], self.utmjd_array[i])
        self.assertAlmostEqual(s1, self.utmjd_array[0])
        self.assertAlmostEqual(s2, self.utmjd_array[0])
        self.assertAlmostEqual(s3, self.utmjd_array[0])
        self.assertAlmostEqual(s4, self.utmjd_array[0])

    def test_ut_to_datetime(self):
        """
        Tests the array and scalar based methods of converting various times to datetime
        These all should give the same answer.
        """

        t1 = ut_to_datetime(self.utobj_array)
        t2 = ut_to_datetime(self.utstr_array)
        t3 = ut_to_datetime(self.utd64_array)
        t4 = ut_to_datetime(self.utmjd_array)
        s1 = ut_to_datetime(self.utobj_array[0]) - self.utobj_array[0]
        s2 = ut_to_datetime(self.utstr_array[0]) - self.utobj_array[0]
        s3 = ut_to_datetime(self.utd64_array[0]) - self.utobj_array[0]
        s4 = ut_to_datetime(self.utmjd_array[0]) - self.utobj_array[0]
        for i in range(3):
            dt1 = t1[i] - self.utobj_array[i]
            dt2 = t2[i] - self.utobj_array[i]
            dt3 = t3[i] - self.utobj_array[i]
            dt4 = t4[i] - self.utobj_array[i]
            self.assertEqual(abs(dt1.microseconds), 0)
            self.assertEqual(abs(dt2.microseconds), 0)
            self.assertEqual(abs(dt3.microseconds), 0)
            self.assertLessEqual(abs(dt4.microseconds), 2)
        self.assertEqual(abs(s1.microseconds), 0)
        self.assertEqual(abs(s2.microseconds), 0)
        self.assertEqual(abs(s3.microseconds), 0)
        self.assertLessEqual(abs(s4.microseconds), 2)

    def test_ut_to_datetime64(self):
        """
        Tests the array and scalar based methods of converting various times to datetime64.
        These all should give the same answer.
        """

        microsec = np.timedelta64(1, 'us')
        t1 = ut_to_datetime64(self.utobj_array)
        t2 = ut_to_datetime64(self.utstr_array)
        t3 = ut_to_datetime64(self.utd64_array)
        t4 = ut_to_datetime64(self.utmjd_array)
        s1 = (ut_to_datetime64(self.utobj_array[0]) - self.utd64_array[0]) / microsec
        s2 = (ut_to_datetime64(self.utstr_array[0]) - self.utd64_array[0]) / microsec
        s3 = (ut_to_datetime64(self.utd64_array[0]) - self.utd64_array[0]) / microsec
        s4 = (ut_to_datetime64(self.utmjd_array[0]) - self.utd64_array[0]) / microsec
        for i in range(3):
            dt1 = (t1[i] - self.utd64_array[i]) / microsec
            dt2 = (t2[i] - self.utd64_array[i]) / microsec
            dt3 = (t3[i] - self.utd64_array[i]) / microsec
            dt4 = (t4[i] - self.utd64_array[i]) / microsec
            self.assertEqual(abs(dt1), 0)
            self.assertEqual(abs(dt2), 0)
            self.assertEqual(abs(dt3), 0)
            self.assertLessEqual(abs(dt4), 2)
        self.assertEqual(abs(s1), 0)
        self.assertEqual(abs(s2), 0)
        self.assertEqual(abs(s3), 0)
        self.assertLessEqual(abs(s4), 2)


if __name__ == '__main__':
    unittest.main()
