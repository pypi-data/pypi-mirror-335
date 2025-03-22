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
Tutorial on FullTensor.

"""

import numpy as np
import matplotlib.pyplot as plt
import tensap

np.random.seed(0)

# %% Creation of random FullTensor with precribed shapes
# Order-4 full tensor with i.i.d. entries drawn according to the uniform
# distribution on (0, 1)

TENSOR_1 = tensap.FullTensor.rand([2, 3, 4, 5])
print("TENSOR_1 = tensap.FullTensor.rand([2, 3, 4, 5]) =")
print(TENSOR_1)

# Order-6 full tensor with i.i.d. entries drawn according to the standard
# gaussian distribution
TENSOR_2 = tensap.FullTensor.randn([2, 3, 4, 4, 3, 2])
print("\nTENSOR_2 = tensap.FullTensor.rand([2, 3, 4, 4, 3, 2]) =")
print(TENSOR_2)

print("\nNorm of TENSOR_1 = %f" % TENSOR_1.norm())
print("Number of entries of TENSOR_1 = %i" % TENSOR_1.storage())
print("Number of non-zero entries of TENSOR_1 = %i" % TENSOR_1.sparse_storage())

# %% Operations on FullTensor
# Contraction of the tensors TENSOR_1 and TENSOR_2, in the dimensions 0 and 2,
# and 5 and 3, respectively
# The resulting tensor TENSOR_3 is of order TENSOR_3.order = 4+6-4 = 6, and of
# dimensions TENSOR_3.shape = [3, 5, 2, 3, 4, 3]

TENSOR_3 = TENSOR_1.tensordot(TENSOR_2, [0, 2], [5, 3])
print("\nTENSOR_3 = TENSOR_1.tensordot(TENSOR_2, [0, 2], [5, 3]) =")
print(TENSOR_3)

# Contraction of the tensors TENSOR_1 and TENSOR_2, in the dimensions 0 and 2,
# and 5 and 3, respectively, and evaluation of the diagonal in the dimensions
# 1 and 4, respectively
# The resulting tensor TENSOR_4 is of order TENSOR_4.order = 4+6-4-1 = 5, and
# of dimensions TENSOR_4.shape = [3, 5, 2, 3, 4]
TENSOR_4 = TENSOR_1.tensordot_eval_diag(TENSOR_2, [0, 2], [5, 3], 1, 4)
print(
    "\nTENSOR_4 = TENSOR_1.tensordot_eval_diag(TENSOR_2, [0, 2], " + "[5, 3], 1, 4) ="
)
print(TENSOR_4)

# Outer product of the tensors TENSOR_1 and TENSOR_2 with evaluation of the
# diagonal in the dimensions 2 and 3, respectively
# The resulting tensot TENSOR_5 is such that
# TENSOR_5[i1, i2, k, i4, j1, j2, j3, j5, j6] = TENSOR_1[i1, i2, k, i4]
# TENSOR_2(j1, j2, j3, k, j5, j6)
TENSOR_5 = TENSOR_1.outer_product_eval_diag(TENSOR_2, 2, 3)
print("\nTENSOR_5 = TENSOR_1.outer_product_eval_diag(TENSOR_2, 2, 3) =")
print(TENSOR_5)

# Outer product of the tensors TENSOR_1 and TENSOR_2 with evaluation of several
# diagonals, in the dimensions 1 and 2, and 4 and 3 respectively
# The resulting tensor TENSOR_6 is such that
# TENSOR_6(i1, k, l, i4, j1, j2, j3, j6) = TENSOR_1(i1, k, l, i4)
# TENSOR_2(j1, j2, j3, l, k, j6)
TENSOR_6 = TENSOR_1.outer_product_eval_diag(TENSOR_2, [1, 2], [4, 3], True)
print(
    "\nTENSOR_6 = TENSOR_1.outer_product_eval_diag(TENSOR_2, [1, 2], "
    + "[4, 3], True) ="
)
print(TENSOR_6)

# %% Orthogonalization of a FullTensor
# The tensor TENSOR_7 is of same shape and order at TENSOR_4, but is such that
# its  {2}-matricization, denoted by MAT_TENSOR_7, verifies
# np.matmul(MAT_TENSOR_7, np.transpose(MAT_TENSOR_7)) =
# np.eye(TENSOR_4.shape[2])
TENSOR_7 = TENSOR_4.orth(2)[0]
print("\nTENSOR_7 = TENSOR_4.orth(2) =")
print(TENSOR_7)

# We check the orthogonality by computing the product of the {2}-matricization
# of TENSOR_7 by itself
MAT_TENSOR_7 = TENSOR_7.matricize(2)
P = MAT_TENSOR_7.tensordot(MAT_TENSOR_7, 1, 1)
print("\nChecking the orthogonality condition on TENSOR_7:")
print(P.data)

# %% Singular values of a FullTensor
SIN_VAL = TENSOR_3.singular_values()

ORDER = TENSOR_3.order
SIZE_2 = int(np.floor(np.sqrt(ORDER)))
SIZE_1 = int(np.ceil(ORDER / SIZE_2))
for nb_plot in np.arange(1, ORDER + 1):
    plt.subplot(SIZE_1, SIZE_2, nb_plot)
    plt.bar(range(SIN_VAL[nb_plot - 1].size), SIN_VAL[nb_plot - 1])
    plt.title("%i-singular values" % (nb_plot - 1))
plt.show()

# %% Conversion of a FullTensor into a SparseTensor
# The TENSOR_8 is a tensor of order 3 and shape (3,4,2) containing only 0's and 1's.
# It is filled randomly with proba 2/3 for 0's and 1/3 for 1's.
# This tensor is then converted into a SparseTensor using the method sparse().
TENSOR_8 = tensap.FullTensor(
    np.random.choice([0, 1], size=24, p=[2 / 3, 1 / 3]).reshape((3, 4, 2))
)
print(f"\nTENSOR_8 has a storage complexity of {TENSOR_8.storage()}")
print(f"It has a sparse storage complexity of {TENSOR_8.sparse_storage()}")
print(
    f"Its sparse conversion has a storage complexity of {TENSOR_8.sparse().storage()}"
)

# %% Evaluation at indices
x = tensap.FullTensor.rand([4, 4, 4])
print("[x(1,2,3) x(2,3,2)] = ", x.eval_at_indices([[1, 2, 3], [2, 3, 2]]))
print("x(1,2,:) = ", x.eval_at_indices([1, 2], [0, 1]))

# %% Sum along given dimensions
x = tensap.FullTensor.rand([2, 3, 4, 5])
print("Initial tensor x")
print(x)
print("Sum of x over all dimensions")
print(x.reduce_sum())
print("Sum of x along dimension 0")
x1 = x.reduce_sum(0)
print(x1)
print("Sum of x along dimensions 1 and 3")
x2 = x.reduce_sum((1, 3))
print(x2)
print("Squeeze the resulting tensor (removing modes with size 1)")
print(x2.squeeze())
