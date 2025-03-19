# I did not manage to move everything to pyproject, because of the need
# to use np.get_include()
# It is apparently relatively standard, cf
# https://packaging.python.org/en/latest/guides/modernize-setup-py-project/#should-setup-py-be-deleted

from codecs import open
from os import path

import numpy as np
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from setuptools import Extension, setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

extensions = cythonize(
    list(
        Extension(
            f"pyezzi.{f}",
            [f"pyezzi/{f}.pyx"],
            extra_compile_args=["-fopenmp", "-O3"],
            extra_link_args=["-fopenmp"],
        )
        for f in ("laplace", "yezzi")
    )
)

cmdclass = {"build_ext": build_ext}

setup(
    ext_modules=extensions,
    packages=["pyezzi"],
    cmdclass=cmdclass,
    include_dirs=[np.get_include()],
)
