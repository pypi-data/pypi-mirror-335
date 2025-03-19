#!/usr/bin/env python

import logging
import os
import os.path
import unittest

import numpy as np
from skimage.io import imread

from pyezzi.thickness import ThicknessSolver


class Pyezzi3DResultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        image_dir = os.path.join(os.path.dirname(dir_path), "example")
        epi = imread(os.path.join(image_dir, "epi.tif")).astype(bool)
        wall = imread(os.path.join(image_dir, "wall.tif")).astype(bool)

        labeled_image = np.zeros_like(epi, np.uint8)
        labeled_image[epi] = 1
        labeled_image[wall] = 2

        cls.solver = ThicknessSolver(
            labeled_image,
            spacing=[1, 1, 1],
            label_inside=1,
            label_wall=2,
            label_holes=3,
            laplace_tolerance=0,
            laplace_max_iter=5000,
            yezzi_tolerance=0,
            yezzi_max_iter=5000,
        )

        # np.savez(os.path.join(dir_path, "3d_results.npz"),
        #          thickness=cls.solver.result,
        #          L0=cls.solver.L0,
        #          L1=cls.solver.L1,
        #          laplace=cls.solver.laplace_grid)
        cls.reference = np.load(os.path.join(dir_path, "3d_results.npz"))

    def testL0(self):
        self.assertTrue(np.allclose(self.reference["L0"], self.solver.L0))

    def testL1(self):
        self.assertTrue(np.allclose(self.reference["L1"], self.solver.L1))

    def testThickness(self):
        self.assertTrue(np.allclose(self.reference["thickness"], self.solver.result))

    def testLaplace(self):
        self.assertTrue(
            np.allclose(self.reference["laplace"], self.solver.laplace_grid)
        )


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)02d:%(levelname)s:%(message)s",
    datefmt="%H:%M:%S",
)

if __name__ == "__main__":
    unittest.main()
