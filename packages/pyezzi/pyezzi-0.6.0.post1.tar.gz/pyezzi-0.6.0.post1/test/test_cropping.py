#!/usr/bin/env python

import unittest

import numpy as np

from pyezzi.cropping import crop_array, restore_array


class CropperTests(unittest.TestCase):
    def test_3d_no_crop_needed(self):
        array = np.ones((8, 9, 10))
        cropped, restore_padding = crop_array(array)
        self.assertTrue(cropped.shape == (10, 11, 12))
        restored = restore_array(cropped, restore_padding)
        self.assertTrue(np.array_equal(array, restored))

    def test_2d_no_crop_needed(self):
        array = np.ones((8, 9))
        cropped, restore_padding = crop_array(array)
        self.assertTrue(cropped.shape == (10, 11))
        restored = restore_array(cropped, restore_padding)
        self.assertTrue(np.array_equal(array, restored))

    def test_2d(self):
        array = np.zeros((8, 9))
        array[4:8, 3:4] = 1
        cropped, restore_padding = crop_array(array)
        self.assertTrue(cropped.shape == (6, 3))
        restored = restore_array(cropped, restore_padding)
        self.assertTrue(np.array_equal(array, restored))

    def test_3d(self):
        array = np.zeros((8, 9, 80))
        array[4:8, 3:4, 44:] = 1
        cropped, restore_padding = crop_array(array)
        restored = restore_array(cropped, restore_padding)
        self.assertTrue(np.array_equal(array, restored))


if __name__ == "__main__":
    unittest.main()
