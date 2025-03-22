# Copyright (c) 2020, Anthony Nouy, Erwan Grelier
# This file is part of tensap (tensor approximation package).

# tensap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# tensap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with tensap.  If not, see <https://www.gnu.org/licenses/>.

"""
Module utils.

"""

import numpy as np


def fast_intersect(a, b):
    aux = np.concatenate((a, b))
    aux.sort()
    mask = aux[1:] == aux[:-1]
    return aux[:-1][mask]


def fast_setdiff(a, b):
    return a[np.logical_not(np.isin(a, b, assume_unique=True))]


def integer2baseb(i, b, d=None):
    """
    Returns the representation [i_1, ..., i_d] in base b of a set of non
    negative integers i = sum_{k=1}^d i_k b^(d-k) in [0, b^d-1].

    Parameters
    ----------
    i : list or numpy.ndarray
        The integers to be convertes in base b.
    b : int
        The base.
    d : int, optional
        The dimension. The default is the minimal integer allowing the
        representation of max(i).

    Returns
    -------
    numpy.ndarray
        The representation [i_1, ..., i_d] in base b of the integers.

    """
    if d is None:
        d = int(np.ceil(np.log(np.max(i) + 1) / np.log(b)))

    I0 = np.unravel_index(np.ravel(i), np.full(d, b), order="F")
    return np.fliplr(np.transpose(np.array(I0)))


def baseb2integer(I0, b):
    """
    Return the integers with given representations in base b.

    Parameters
    ----------
    I : numpy.ndarray or list
        A row of I contains d integers [i_1, ..., i_d] in {0, ..., b-1}
        associated with an integer i = sum_{k=1}^d i_k b^(d-k) in [0, b^d-1].
    b : int
        The base.

    Returns
    -------
    numpy.ndarray
        The integers with given representations in base b.

    """
    I0 = np.atleast_2d(I0)
    d = I0.shape[1]
    I0 = np.fliplr(I0)
    I0 = np.transpose(I0)
    return np.ravel_multi_index(I0, np.full(d, b), order="F")
