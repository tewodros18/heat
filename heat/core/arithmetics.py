from __future__ import annotations

import torch

from .communication import MPI
from .dndarray import DNDarray
from . import factories
from . import _operations
from . import stride_tricks
from .types import datatype, heat_type_of, heat_type_is_inexact, heat_type_is_exact


__all__ = [
    "add",
    "bitwise_and",
    "bitwise_not",
    "bitwise_or",
    "bitwise_xor",
    "cumprod",
    "cumproduct",
    "cumsum",
    "diff",
    "div",
    "divide",
    "floordiv",
    "floor_divide",
    "fmod",
    "invert",
    "left_shift",
    "mod",
    "mul",
    "multiply",
    "pow",
    "power",
    "prod",
    "remainder",
    "right_shift",
    "sub",
    "subtract",
    "sum",
]


def add(t1, t2) -> DNDarray:
    """
    Element-wise addition of values from two operands, commutative.
    Takes the first and second operand (scalar or :class:`~heat.core.dndarray.DNDarray`) whose elements are to be added
    as argument and returns a ``DNDarray`` containing the results of element-wise addition of ``t1`` and ``t2``.

    Parameters
    ----------
    t1: DNDarray or scalar
        The first operand involved in the addition
    t2: DNDarray or scalar
        The second operand involved in the addition

    Example
    ---------
    >>> import heat as ht
    >>> ht.add(1.0, 4.0)
    tensor([5.])
    >>> T1 = ht.float32([[1, 2], [3, 4]])
    >>> T2 = ht.float32([[2, 2], [2, 2]])
    >>> ht.add(T1, T2)
    tensor([[3., 4.],
            [5., 6.]])
    >>> s = 2.0
    >>> ht.add(T1, s)
    tensor([[3., 4.],
            [5., 6.]])

    """
    return _operations.__binary_op(torch.add, t1, t2)


DNDarray.__add__ = lambda self, other: add(self, other)
DNDarray.__add__.__doc__ = add.__doc__
DNDarray.__radd__ = lambda self, other: add(self, other)
DNDarray.__radd__.__doc__ = add.__doc__


def bitwise_and(t1, t2) -> DNDarray:
    """
    Compute the bit-wise AND of two :class:`~heat.core.dndarray.DNDarray` ``t1`` and ``t2`` element-wise.
    Only integer and boolean types are handled. If ``x1.shape!=x2.shape``, they must be broadcastable to a common shape
    (which becomes the shape of the output)

    Parameters
    ----------
    t1: DNDarray or scalar
        Input tensor
    t2: DNDarray or scalar
        Input tensor

    Example
    ---------
    >>> ht.bitwise_and(13, 17)
    tensor([1])
    >>> ht.bitwise_and(14, 13)
    tensor([12])
    >>> ht.bitwise_and(ht.array([14,3]), 13)
    tensor([12,  1])
    >>> ht.bitwise_and(ht.array([11,7]), ht.array([4,25]))
    tensor([0, 1])
    >>> ht.bitwise_and(ht.array([2,5,255]), ht.array([3,14,16]))
    tensor([ 2,  4, 16])
    >>> ht.bitwise_and(ht.array([True, True]), ht.array([False, True]))
    tensor([False,  True])
    """
    dtypes = (heat_type_of(t1), heat_type_of(t2))

    for dt in dtypes:
        if heat_type_is_inexact(dt):
            raise TypeError("Operation is not supported for float types")

    return _operations.__binary_op(torch.Tensor.__and__, t1, t2)


DNDarray.__and__ = lambda self, other: bitwise_and(self, other)
DNDarray.__and__.__doc__ = bitwise_and.__doc__


def bitwise_or(t1, t2) -> DNDarray:
    """
    Compute the bit-wise OR of two :class:`~heat.core.dndarray.DNDarray` ``t1`` and ``t2`` element-wise.
    Only integer and boolean types are handled. If ``x1.shape!=x2.shape``, they must be broadcastable to a common shape
    (which becomes the shape of the output)

    Parameters
    ----------
    t1: DNDarray or scalar
        Input tensor
    t2: DNDarray or scalar
        Input tensor

    Example
    ---------
    >>> ht.bitwise_or(13, 16)
    tensor([29])
    >>> ht.bitwise_or(32, 2)
    tensor([34])
    >>> ht.bitwise_or(ht.array([33, 4]), 1)
    tensor([33,  5])
    >>> ht.bitwise_or(ht.array([33, 4]), ht.array([1, 2]))
    tensor([33,  6])
    >>> ht.bitwise_or(ht.array([2, 5, 255]), ht.array([4, 4, 4]))
    tensor([  6,   5, 255])
    >>> ht.bitwise_or(ht.array([2, 5, 255, 2147483647], dtype=ht.int32),
    ...               ht.array([4, 4, 4, 2147483647], dtype=ht.int32))
    tensor([         6,          5,        255, 2147483647])
    >>> ht.bitwise_or(ht.array([True, True]), ht.array([False, True]))
    tensor([ True,  True])
    """
    dtypes = (heat_type_of(t1), heat_type_of(t2))

    for dt in dtypes:
        if heat_type_is_inexact(dt):
            raise TypeError("Operation is not supported for float types")

    return _operations.__binary_op(torch.Tensor.__or__, t1, t2)


DNDarray.__or__ = lambda self, other: bitwise_or(self, other)
DNDarray.__or__.__doc__ = bitwise_or.__doc__


def bitwise_xor(t1, t2) -> DNDarray:
    """
    Compute the bit-wise XOR of two arrays element-wise ``t1`` and ``t2``.
    Only integer and boolean types are handled. If ``x1.shape!=x2.shape``, they must be broadcastable to a common shape
    (which becomes the shape of the output)

    Parameters
    ----------
    t1: DNDarray or scalar
        Input tensor
    t2: DNDarray or scalar
        Input tensor

    Example
    ---------
    >>> ht.bitwise_xor(13, 17)
    tensor([28])
    >>> ht.bitwise_xor(31, 5)
    tensor([26])
    >>> ht.bitwise_xor(ht.array[31,3], 5)
    tensor([26,  6])
    >>> ht.bitwise_xor(ht.array([31,3]), ht.array([5,6]))
    tensor([26,  5])
    >>> ht.bitwise_xor(ht.array([True, True]), ht.array([False, True]))
    tensor([ True, False])
    """
    dtypes = (heat_type_of(t1), heat_type_of(t2))

    for dt in dtypes:
        if heat_type_is_inexact(dt):
            raise TypeError("Operation is not supported for float types")

    return _operations.__binary_op(torch.Tensor.__xor__, t1, t2)


DNDarray.__xor__ = lambda self, other: bitwise_xor(self, other)
DNDarray.__xor__.__doc__ = bitwise_xor.__doc__


def cumprod(a, axis, dtype=None, out=None) -> DNDarray:
    """
    Return the cumulative product of elements along a given axis.

    Parameters
    ----------
    a : DNDarray
        Input array.
    axis : int
        Axis along which the cumulative product is computed.
    dtype : datatype, optional
        Type of the returned array, as well as of the accumulator in which
        the elements are multiplied.  If ``dtype`` is not specified, it
        defaults to the datatype of ``a``, unless ``a`` has an integer dtype with
        a precision less than that of the default platform integer.  In
        that case, the default platform integer is used instead.
    out : DNDarray, optional
        Alternative output array in which to place the result. It must
        have the same shape and buffer length as the expected output
        but the type of the resulting values will be cast if necessary.

    Example
    --------
    >>> a = ht.full((3,3), 2)
    >>> ht.cumprod(a, 0)
    tensor([[2., 2., 2.],
            [4., 4., 4.],
            [8., 8., 8.])
    """
    return _operations.__cum_op(a, torch.cumprod, MPI.PROD, torch.mul, 1, axis, dtype, out)


# Alias support
cumproduct = cumprod


def cumsum(a, axis, dtype=None, out=None) -> DNDarray:
    """
    Return the cumulative sum of the elements along a given axis.

    Parameters
    ----------
    a : DNDarray
        Input array.
    axis : int
        Axis along which the cumulative sum is computed.
    dtype : datatype, optional
        Type of the returned array and of the accumulator in which the
        elements are summed.  If ``dtype`` is not specified, it defaults
        to the datatype of ``a``, unless ``a`` has an integer dtype with a
        precision less than that of the default platform integer.  In
        that case, the default platform integer is used.
    out : DNDarray, optional
        Alternative output array in which to place the result. It must
        have the same shape and buffer length as the expected output
        but the type will be cast if necessary.

    Example
    --------
    >>> a = ht.ones((3,3))
    >>> ht.cumsum(a, 0)
    tensor([[1., 1., 1.],
            [2., 2., 2.],
            [3., 3., 3.])
    """
    return _operations.__cum_op(a, torch.cumsum, MPI.SUM, torch.add, 0, axis, dtype, out)


def diff(a, n=1, axis=-1) -> DNDarray:
    """
    Calculate the n-th discrete difference along the given axis.
    The first difference is given by ``out[i]=a[i+1]-a[i]`` along the given axis, higher differences are calculated
    by using diff recursively. The shape of the output is the same as ``a`` except along axis where the dimension is smaller
    by ``n``. The datatype of the output is the same as the datatype of the difference between any two elements of ``a``.
    The split does not change. The output array is balanced.

    Parameters
    -------
    a : DNDarray
        Input array
    n : int, optional
        The number of times values are differenced. If zero, the input is returned as-is.
        ``n=2`` is equivalent to ``diff(diff(a))``
    axis : int, optional
        The axis along which the difference is taken, default is the last axis.
    """
    if n == 0:
        return a
    if n < 0:
        raise ValueError("diff requires that n be a positive number, got {}".format(n))
    if not isinstance(a, DNDarray):
        raise TypeError("'a' must be a DNDarray")

    axis = stride_tricks.sanitize_axis(a.gshape, axis)

    if not a.is_distributed():
        ret = a.copy()
        for _ in range(n):
            axis_slice = [slice(None)] * len(ret.shape)
            axis_slice[axis] = slice(1, None, None)
            axis_slice_end = [slice(None)] * len(ret.shape)
            axis_slice_end[axis] = slice(None, -1, None)
            ret = ret[tuple(axis_slice)] - ret[tuple(axis_slice_end)]
        return ret

    size = a.comm.size
    rank = a.comm.rank
    ret = a.copy()
    # work loop, runs n times. using the result at the end of the loop as the starting values for each loop
    for _ in range(n):
        axis_slice = [slice(None)] * len(ret.shape)
        axis_slice[axis] = slice(1, None, None)
        axis_slice_end = [slice(None)] * len(ret.shape)
        axis_slice_end[axis] = slice(None, -1, None)

        # build the slice for the first element on the specified axis
        arb_slice = [slice(None)] * len(a.shape)
        arb_slice[axis] = 0
        # send the first element of the array to rank - 1
        if rank > 0:
            snd = ret.comm.Isend(ret.lloc[arb_slice].clone(), dest=rank - 1, tag=rank)

        # standard logic for the diff with the next element
        dif = ret.lloc[axis_slice] - ret.lloc[axis_slice_end]
        # need to slice out to select the proper elements of out
        diff_slice = [slice(x) for x in dif.shape]
        ret.lloc[diff_slice] = dif

        if rank > 0:
            snd.wait()  # wait for the send to finish
        if rank < size - 1:
            cr_slice = [slice(None)] * len(a.shape)
            # slice of 1 element in the selected axis for the shape creation
            cr_slice[axis] = 1
            recv_data = torch.ones(
                ret.lloc[cr_slice].shape, dtype=ret.dtype.torch_type(), device=a.device.torch_device
            )
            rec = ret.comm.Irecv(recv_data, source=rank + 1, tag=rank + 1)
            axis_slice_end = [slice(None)] * len(a.shape)
            # select the last elements in the selected axis
            axis_slice_end[axis] = slice(-1, None)
            rec.wait()
            # diff logic
            ret.lloc[axis_slice_end] = (
                recv_data.reshape(ret.lloc[axis_slice_end].shape) - ret.lloc[axis_slice_end]
            )

    axis_slice_end = [slice(None, None, None)] * len(a.shape)
    axis_slice_end[axis] = slice(None, -1 * n, None)
    ret = ret[tuple(axis_slice_end)]  # slice off the last element on the array (nonsense data)
    ret.balance_()  # balance the array before returning
    return ret


def div(t1, t2) -> DNDarray:
    """
    Element-wise true division of values of operand ``t1`` by values of operands ``t2`` (i.e ``t1/t2``).
    Operation is not commutative.

    Parameters
    ----------
    t1: DNDarray or scalar
        The first operand whose values are divided
    t2: DNDarray or scalar
        The second operand by whose values is divided

    Example
    ---------
    >>> ht.div(2.0, 2.0)
    tensor([1.])
    >>> T1 = ht.float32([[1, 2], [3, 4]])
    >>> T2 = ht.float32([[2, 2], [2, 2]])
    >>> ht.div(T1, T2)
    tensor([[0.5000, 1.0000],
            [1.5000, 2.0000]])
    >>> s = 2.0
    >>> ht.div(s, T1)
    tensor([[2.0000, 1.0000],
            [0.6667, 0.5000]])
    """
    return _operations.__binary_op(torch.true_divide, t1, t2)


DNDarray.__truediv__ = lambda self, other: div(self, other)
DNDarray.__truediv__.__doc__ = div.__doc__
DNDarray.__rtruediv__ = lambda self, other: div(other, self)
DNDarray.__rtruediv__.__doc__ = div.__doc__

# Alias in compliance with numpy API
divide = div


def fmod(t1, t2) -> DNDarray:
    """
    Element-wise division remainder of values of operand ``t1`` by values of operand ``t2`` (i.e. C Library function fmod).
    Result has the sign as the dividend ``t1``. Operation is not commutative.

    Parameters
    ----------
    t1: DNDarray or scalar
        The first operand whose values are divided (may be floats)
    t2: DNDarray or scalar
        The second operand by whose values is divided (may be floats)

    Example
    ---------
    >>> ht.fmod(2.0, 2.0)
    tensor([0.])
    >>> T1 = ht.float32([[1, 2], [3, 4]])
    >>> T2 = ht.float32([[2, 2], [2, 2]])
    >>> ht.fmod(T1, T2)
    tensor([[1., 0.],
            [1., 0.]])
    >>> s = 2.0
    >>> ht.fmod(s, T1)
    tensor([[0., 0.]
            [2., 2.]])
    """
    return _operations.__binary_op(torch.fmod, t1, t2)


def floordiv(t1, t2) -> DNDarray:
    """
    Element-wise floor division of value of operand ``t1`` by values of operands ``t2`` (i.e. ``t1//t2``), not commutative.

    Parameters
    ----------
    t1: DNDarray or scalar
        The first operand whose values are divided
    t2: DNDarray or scalar
        The second operand by whose values is divided

    Example
    ---------
    >>> T1 = ht.float32([[1.7, 2.0], [1.9, 4.2]])
    >>> ht.floordiv(T1, 1)
    tensor([[1., 2.],
            [1., 4.]])
    >>> T2 = ht.float32([1.5, 2.5])
    >>> ht.floordiv(T1, T2)
    tensor([[1., 0.],
            [1., 1.]])
    """
    return _operations.__binary_op(torch.floor_divide, t1, t2)


DNDarray.__floordiv__ = lambda self, other: floordiv(self, other)
DNDarray.__floordiv__.__doc__ = floordiv.__doc__
DNDarray.__rfloordiv__ = lambda self, other: floordiv(other, self)
DNDarray.__rfloordiv__.__doc__ = floordiv.__doc__

# Alias in compliance with numpy API
floor_divide = floordiv


def invert(t, out=None) -> DNDarray:
    """
    Computes the bitwise NOT of the given input :class:`~heat.core.dndarray.DNDarray`. The input array must be of integral
    or Boolean types. For boolean arrays, it computes the logical NOT. Bitwise_not is an alias for invert.

    Parameters
    ---------
    t: DNDarray
        The input array to invert. Must be of integral or Boolean types
    out : DNDarray, optional
        Alternative output array in which to place the result. It must have the same shape as the expected output.

    Example
    ---------
    >>> ht.invert(ht.array([13], dtype=ht.uint8))
    tensor([242], dtype=ht.uint8)
    >>> ht.bitwise_not(ht.array([-1, -2, 3], dtype=ht.int8))
    tensor([ 0,  1, -4], dtype=ht.int8)
    """
    dt = heat_type_of(t)

    if heat_type_is_inexact(dt):
        raise TypeError("Operation is not supported for float types")

    return _operations.__local_op(torch.bitwise_not, t, out, no_cast=True)


DNDarray.__invert__ = lambda self, out=None: invert(self, out)
DNDarray.__invert__.__doc__ = invert.__doc__

# alias for invert
bitwise_not = invert


def left_shift(t1, t2) -> DNDarray:
    """
    Shift the bits of an integer to the left.

    Parameters
    ----------
    t1: DNDarray
        Input tensor
    t2: DNDarray or scalar
        Integer number of zero bits to add

    Example
    ---------
    >>> ht.left_shift(ht.array[1,2,3], 1)
    tensor([2, 4, 6])
    """
    dtypes = (heat_type_of(t1), heat_type_of(t2))

    for dt in dtypes:
        if heat_type_is_inexact(dt):
            raise TypeError("Operation is not supported for float types")

    return _operations.__binary_op(torch.Tensor.__lshift__, t1, t2)


DNDarray.__lshift__ = lambda self, other: left_shift(self, other)
DNDarray.__lshift__.__doc__ = left_shift.__doc__


def mod(t1, t2) -> DNDarray:
    """
    Element-wise division remainder of values of operand ``t1`` by values of operand ``t2`` (i.e. ``t1%t2``).
    Operation is not commutative. Result has the same sign as the devisor ``t2``.
    Currently ``t1`` and ``t2`` are just passed to remainder.

    Parameters
    ----------
    t1: DNDarray or scalar
        The first operand whose values are divided
    t2: DNDarray or scalar
        The second operand by whose values is divided

    Example
    ---------
    >>> ht.mod(2, 2)
    tensor([0])
    >>> T1 = ht.int32([[1, 2], [3, 4]])
    >>> T2 = ht.int32([[2, 2], [2, 2]])
    >>> ht.mod(T1, T2)
    tensor([[1, 0],
            [1, 0]], dtype=torch.int32)
    >>> s = 2
    >>> ht.mod(s, T1)
    tensor([[0, 0]
            [2, 2]], dtype=torch.int32)
    """
    return remainder(t1, t2)


DNDarray.__mod__ = lambda self, other: mod(self, other)
DNDarray.__mod__.__doc__ = mod.__doc__
DNDarray.__rmod__ = lambda self, other: mod(other, self)
DNDarray.__rmod__.__doc__ = mod.__doc__


def mul(t1, t2) -> DNDarray:
    """
    Element-wise multiplication (NOT matrix multiplication) of values from two operands, commutative.
    Takes the first and second operand (scalar or :class:`~heat.core.dndarray.DNDarray`) whose elements are to be
    multiplied as argument.

    Parameters
    ----------
    t1: DNDarray or scalar
        The first operand involved in the multiplication
    t2: DNDarray or scalar
        The second operand involved in the multiplication

    Example
    ---------
    >>> ht.mul(2.0, 4.0)
    tensor([8.])
    >>> T1 = ht.float32([[1, 2], [3, 4]])
    >>> s = 3.0
    >>> ht.mul(T1, s)
    tensor([[3., 6.],
            [9., 12.]])

    >>> T2 = ht.float32([[2, 2], [2, 2]])
    >>> ht.mul(T1, T2)
    tensor([[2., 4.],
            [6., 8.]])
    >>> T2 = ht.float32([[2, 2], [2, 2]])
    >>> ht.mul(T1, T2)
    tensor([[2., 4.],
            [6., 8.]])
    """
    return _operations.__binary_op(torch.mul, t1, t2)


DNDarray.__mul__ = lambda self, other: mul(self, other)
DNDarray.__mul__.__doc__ = mul.__doc__
DNDarray.__rmul__ = lambda self, other: mul(self, other)
DNDarray.__rmul__.__doc__ = mul.__doc__

# Alias in compliance with numpy API
multiply = mul


def pow(t1, t2) -> DNDarray:
    """
    Element-wise exponential function of values of operand ``t1`` to the power of values of operand ``t2`` (i.e ``t1**t2``).
    Operation is not commutative.

    Parameters
    ----------
    t1: DNDarray or scalar
        The first operand whose values represent the base
    t2: DNDarray or scalar
        The second operand by whose values represent the exponent

    Example
    ---------
    >>> ht.pow (3.0, 2.0)
    tensor([9.])
    >>> T1 = ht.float32([[1, 2], [3, 4]])
    >>> T2 = ht.float32([[3, 3], [2, 2]])
    >>> ht.pow(T1, T2)
    tensor([[1., 8.],
            [9., 16.]])
    >>> s = 3.0
    >>> ht.pow(T1, s)
    tensor([[1., 8.],
            [27., 64.]])
    """
    return _operations.__binary_op(torch.pow, t1, t2)


DNDarray.__pow__ = lambda self, other: pow(self, other)
DNDarray.__pow__.__doc__ = pow.__doc__
DNDarray.__rpow__ = lambda self, other: pow(other, self)
DNDarray.__rpow__.__doc__ = pow.__doc__


# Alias in compliance with numpy API
power = pow


def remainder(t1, t2) -> DNDarray:
    """
    Element-wise division remainder of values of operand ``t1`` by values of operand ``t2`` (i.e. ``t1%t2``).
    Operation is not commutative. Result has the same sign as the devisor ``t2``.

    Parameters
    ----------
    t1: DNDarray or scalar
        The first operand whose values are divided
    t2: DNDarray or scalar
        The second operand by whose values is divided

    Example
    ---------
    >>> ht.mod(2, 2)
    tensor([0])
    >>> T1 = ht.int32([[1, 2], [3, 4]])
    >>> T2 = ht.int32([[2, 2], [2, 2]])
    >>> ht.mod(T1, T2)
    tensor([[1, 0],
            [1, 0]], dtype=torch.int32)
    >>> s = 2
    >>> ht.mod(s, T1)
    tensor([[0, 0]
            [2, 2]], dtype=torch.int32)
    """
    return _operations.__binary_op(torch.remainder, t1, t2)


def right_shift(t1, t2) -> DNDarray:
    """
    Shift the bits of an integer to the right.

    Parameters
    ----------
    t1: DNDarray or scalar
        Input array
    t2: DNDarray or scalar
        Integer number of bits to remove

    Example
    ---------
    >>> ht.right_shift(ht.array[1,2,3], 1)
    tensor([0, 1, 1])
    """
    dtypes = (heat_type_of(t1), heat_type_of(t2))

    for dt in dtypes:
        if not heat_type_is_exact(dt):
            raise TypeError("Operation is supported for integer types only")

    return _operations.__binary_op(torch.Tensor.__rshift__, t1, t2)


DNDarray.__rshift__ = lambda self, other: right_shift(self, other)
DNDarray.__rshift__.__doc__ = right_shift.__doc__


def prod(x, axis=None, out=None, keepdim=None) -> DNDarray:
    """
    Return the product of array elements over a given axis in form of an array shaped as a but with the specified axis removed.

    Parameters
    ----------
    x : DNDarray
        Input array.
    axis : None or int or Tuple[int,...], optional
        Axis or axes along which a product is performed. The default, ``axis=None``, will calculate the product of all the
        elements in the input array. If axis is negative it counts from the last to the first axis.
        If axis is a tuple of ints, a product is performed on all of the axes specified in the tuple instead of a single
        axis or all the axes as before.
    out : DNDarray, optional
        Alternative output array in which to place the result. It must have the same shape as the expected output, but
        the datatype of the output values will be cast if necessary.
    keepdims : bool, optional
        If this is set to ``True``, the axes which are reduced are left in the result as dimensions with size one. With this
        option, the result will broadcast correctly against the input array.

    Example
    --------
    >>> ht.prod([1.,2.])
    ht.tensor([2.0])
    >>> ht.prod([
        [1.,2.],
        [3.,4.]
    ])
    ht.tensor([24.0])
    >>> ht.prod([
        [1.,2.],
        [3.,4.]
    ], axis=1)
    ht.tensor([  2.,  12.])
    """
    return _operations.__reduce_op(
        x, torch.prod, MPI.PROD, axis=axis, out=out, neutral=1, keepdim=keepdim
    )


DNDarray.prod = lambda self, axis=None, out=None, keepdim=None: prod(self, axis, out, keepdim)
DNDarray.prod.__doc__ = prod.__doc__


def sub(t1, t2) -> DNDarray:
    """
    Element-wise subtraction of values of operand ``t2`` from values of operands ``t1`` (i.e ``t1-t2``)
    Operation is not commutative.

    Parameters
    ----------
    t1: DNDarray or scalar
        The first operand from which values are subtracted
    t2: DNDarray or scalar
        The second operand whose values are subtracted

    Example
    ---------
    >>> ht.sub(4.0, 1.0)
    tensor([3.])
    >>> T1 = ht.float32([[1, 2], [3, 4]])
    >>> T2 = ht.float32([[2, 2], [2, 2]])
    >>> ht.sub(T1, T2)
    tensor([[-1., 0.],
            [1., 2.]])
    >>> s = 2.0
    >>> ht.sub(s, T1)
    tensor([[ 1.,  0.],
            [-1., -2.]])
    """
    return _operations.__binary_op(torch.sub, t1, t2)


DNDarray.__sub__ = lambda self, other: sub(self, other)
DNDarray.__sub__.__doc__ = sub.__doc__
DNDarray.__rsub__ = lambda self, other: sub(other, self)
DNDarray.__rsub__.__doc__ = sub.__doc__


# Alias in compliance with numpy API
subtract = sub


def sum(x, axis=None, out=None, keepdim=None) -> DNDarray:
    """
    Sum of array elements over a given axis. An array with the same shape as ``self.__array`` except for the specified
    axis which becomes one, e.g. ``a.shape=(1, 2, 3)`` => ``ht.ones((1, 2, 3)).sum(axis=1).shape=(1, 1, 3)``

    Parameters
    ----------
    x : DNDarray
        Input array.
    axis : None or int or Tuple[int,...], optional
        Axis along which a sum is performed. The default, ``axis=None``, will sum all of the elements of the input array.
        If ``axis`` is negative it counts from the last to the first axis. If ``axis`` is a tuple of ints, a sum is performed
        on all of the axes specified in the tuple instead of a single axis or all the axes as before.
    out : DNDarray, optional
        Alternative output array in which to place the result. It must have the same shape as the expected output, but
        the datatype of the output values will be cast if necessary.
    keepdims : bool, optional
        If this is set to ``True``, the axes which are reduced are left in the result as dimensions with size one. With this
        option, the result will broadcast correctly against the input array.

    Example
    --------
    >>> ht.sum(ht.ones(2))
    tensor([2.])
    >>> ht.sum(ht.ones((3,3)))
    tensor([9.])
    >>> ht.sum(ht.ones((3,3)).astype(ht.int))
    tensor([9])
    >>> ht.sum(ht.ones((3,2,1)), axis=-3)
    tensor([[[3.],
             [3.]]])
    """
    # TODO: make me more numpy API complete Issue #101
    return _operations.__reduce_op(
        x, torch.sum, MPI.SUM, axis=axis, out=out, neutral=0, keepdim=keepdim
    )


DNDarray.sum = lambda self, axis=None, out=None, keepdim=None: sum(self, axis, out, keepdim)
