======
pYezzi
======

Compute the thickness of a solid using Yezzi and Prince method described in
the article "An Eulerian PDE Approach for Computing Tissue Thickness", IEEE
TRANSACTIONS ON MEDICAL IMAGING, VOL. 22, NO. 10, OCTOBER 2003. [#]_

A C implementation by Rubén Cárdenes [#]_ helped me a lot writing this,
especially the anisotropic part.

.. [#] http://dx.doi.org/10.1109/tmi.2003.817775
.. [#] http://www.dtic.upf.edu/~rcardenes/Ruben_Cardenes/Software.html


Requirements
============

Runtime: numpy.

Build time: cython.

Test time: scikit-image, scipy.


Installation instruction
========================

Available on pypi. [#]_
Use pip: ``pip install pyezzi``

Alternatively, clone the repository and build cython modules with
``pip install .``.

.. [#]  https://pypi.python.org/pypi/pyezzi

Usage
=====

.. code:: python

    from pyezzi import compute_thickness
    thickness = compute_thickness(labeled_image, debug=True)

``labeled_image`` is a 3 dimensional numpy array where the wall is labeled 2
and the interior is labeled 1.

A ``spacing`` parameter specifying the spacing between voxels along the axes
can optionnaly be specified.

Check out the included jupyter notebooks in the ``example`` folder for more
details.

Note on thickness solver implementation
***************************************

The ordered traversal method mentioned in the original publication can be used
using the ``yezzi_solver='ordered'`` keyword argument. However, we found that
it introduces artifacts to the result. Also the implementation is in pure
python so it is slower to solve than the iterative algorithm.

Contributions
=============

We recommend using [uv](https://docs.astral.sh/uv/) for project management
and [pre-commit](https://pre-commit.com/) to ensure code quality.

After cloning, use `uv sync --frozen --all-groups` to install dev dependencies.
This will set up a virtualenv in `.venv` that you can activate with
`source .venv/bin/activate`. Tests can then be run with `pytest test`.

License
=======

This work is licensed under the french CeCILL license. [#]_
You're free to use and modify the code, but please cite the original paper and
me.

.. [#] https://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
