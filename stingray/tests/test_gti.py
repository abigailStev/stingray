from __future__ import (absolute_import, unicode_literals, division,
                        print_function)

import numpy as np
import pytest
import os

from ..utils import contiguous_regions
from ..gti import cross_gtis, append_gtis, load_gtis, get_btis
from ..gti import check_separate, create_gti_mask
from ..gti import create_gti_from_condition

curdir = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.join(curdir, 'data')

class TestGTI(object):

    """Real unit tests."""

    def test_crossgti1(self):
        """Test the basic working of the intersection of GTIs."""
        gti1 = np.array([[1, 4]])
        gti2 = np.array([[2, 5]])
        newgti = cross_gtis([gti1, gti2])

        assert np.all(newgti == [[2, 4]]), 'GTIs do not coincide!'

    def test_crossgti2(self):
        """A more complicated example of intersection of GTIs."""
        gti1 = np.array([[1, 2], [4, 5], [7, 10], [11, 11.2], [12.2, 13.2]])
        gti2 = np.array([[2, 5], [6, 9], [11.4, 14]])
        newgti = cross_gtis([gti1, gti2])

        assert np.all(newgti == [[4.0, 5.0], [7.0, 9.0], [12.2, 13.2]]), \
            'GTIs do not coincide!'

    def test_bti(self):
        """Test the inversion of GTIs."""
        gti = np.array([[1, 2], [4, 5], [7, 10], [11, 11.2], [12.2, 13.2]])
        bti = get_btis(gti)

        assert np.all(bti == [[2, 4], [5, 7], [10, 11], [11.2, 12.2]]), \
            'BTI is wrong!, %s' % repr(bti)

    def test_gti_mask(self):
        arr = np.array([0, 1, 2, 3, 4, 5, 6])
        gti = np.array([[0, 2.1], [3.9, 5]])
        mask = create_gti_mask(arr, gti)
        # NOTE: the time bin has to be fully inside the GTI. That is why the
        # bin at times 0, 2, 4 and 5 are not in.
        assert np.all(mask == np.array([0, 1, 0, 0, 0, 0, 0], dtype=bool))

    def test_gti_gti_from_condition(self):
        t = np.array([0, 1, 2, 3, 4, 5, 6])
        condition = np.array([1, 1, 0, 0, 1, 0, 0], dtype=bool)
        gti = create_gti_from_condition(t, condition)
        print("gti: " + str(gti))
        assert np.all(gti == np.array([[-0.5, 1.5], [3.5, 4.5]]))

    def test_load_gtis(self):
        """Test event file reading."""
        fname = os.path.join(datadir, 'monol_testA.evt')
        load_gtis(fname, gtistring="GTI")

    def test_check_separate_overlapping_case(self):
        """Test if intersection between two GTIs can be detected. """
        gti1 = np.array([[1, 2], [4, 5], [7, 10], [11, 11.2], [12.2, 13.2]])
        gti2 = np.array([[2, 5], [6, 9], [11.4, 14]])
        assert check_separate(gti1, gti2) == False

    def test_check_separate_nonoverlapping_case(self):
        """Test if two non-overlapping GTIs can be detected."""
        gti1 = np.array([[1, 2], [4, 5]])
        gti2 = np.array([[6, 7], [8, 9]])
        assert check_separate(gti1, gti2) == True

    def test_append_gtis(self):
        """Test if two non-overlapping GTIs can be appended. """
        gti1 = np.array([[1, 2], [4, 5]])
        gti2 = np.array([[6, 7], [8, 9]])
        assert np.all(append_gtis(gti1, gti2) == [[1,2],[4,5],[6,7],[8,9]])

    def test_append_overlapping_gtis(self):
        """Test if exception is raised in event of overlapping gtis."""
        gti1 = np.array([[1, 2], [4, 5]])
        gti2 = np.array([[3, 4.5], [8, 9]])

        with pytest.raises(ValueError):
            append_gtis(gti1, gti2)

