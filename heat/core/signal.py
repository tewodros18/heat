"""Provides a collection of signal-processing operations"""

import torch
from typing import Union, Tuple, Sequence

from .communication import MPI
from .dndarray import DNDarray
from .types import promote_types
from .manipulations import pad, flip
from .factories import array
import torch.nn.functional as fc

__all__ = ["convolve"]


def convolve(a: DNDarray, v: DNDarray, mode: str = "full") -> DNDarray:
    """
    Returns the discrete, linear convolution of two one-dimensional `DNDarray`s.

    Parameters
    ----------
    a : DNDarray
        One-dimensional signal `DNDarray` of shape (N,)
    v : DNDarray
        One-dimensional filter weight `DNDarray` of shape (M,).
    mode : str
        Can be 'full', 'valid', or 'same'. Default is 'full'.
        'full':
          Returns the convolution at
          each point of overlap, with an output shape of (N+M-1,). At
          the end-points of the convolution, the signals do not overlap
          completely, and boundary effects may be seen.
        'same':
          Mode 'same' returns output  of length 'N'. Boundary
          effects are still visible. This mode is not supported for
          even-sized filter weights
        'valid':
          Mode 'valid' returns output of length 'N-M+1'. The
          convolution product is only given for points where the signals
          overlap completely. Values outside the signal boundary have no
          effect.

    Notes
    -----
        Contrary to the original `numpy.convolve`, this function does not
        swap the input arrays if the second one is larger than the first one.
        This is because `a`, the signal, might be memory-distributed,
        whereas the filter `v` is assumed to be non-distributed,
        i.e. a copy of `v` will reside on each process.


    Examples
    --------
    Note how the convolution operator flips the second array
    before "sliding" the two across one another:

    >>> a = ht.ones(10)
    >>> v = ht.arange(3).astype(ht.float)
    >>> ht.convolve(a, v, mode='full')
    DNDarray([0., 1., 3., 3., 3., 3., 2.])
    >>> ht.convolve(a, v, mode='same')
    DNDarray([1., 3., 3., 3., 3.])
    >>> ht.convolve(a, v, mode='valid')
    DNDarray([3., 3., 3.])
    """
    if not isinstance(a, DNDarray):
        try:
            a = array(a)
        except TypeError:
            raise TypeError("non-supported type for signal: {}".format(type(a)))
    if not isinstance(v, DNDarray):
        try:
            v = array(v)
        except TypeError:
            raise TypeError("non-supported type for filter: {}".format(type(v)))
    promoted_type = promote_types(a.dtype, v.dtype)
    a = a.astype(promoted_type)
    v = v.astype(promoted_type)

    if v.is_distributed() and mode == "full" or mode == "same":
        raise TypeError("Distributed filter weights only supportes valid mode")
    if len(a.shape) != 1 or len(v.shape) != 1:
        raise ValueError("Only 1-dimensional input DNDarrays are allowed")
    if a.shape[0] <= v.shape[0]:
        raise ValueError("Filter size must not be greater than or equal to signal size")
    if mode == "same" and v.shape[0] % 2 == 0:
        raise ValueError("Mode 'same' cannot be used with even-sized kernel")

    # compute halo size
    halo_size =int(v.lshape_map[0][0] /2)

    # pad DNDarray with zeros according to mode
    if mode == "full":
        pad_size = v.shape[0] - 1
        gshape = v.shape[0] + a.shape[0] - 1
    elif mode == "same":
        pad_size = halo_size
        gshape = a.shape[0]
    elif mode == "valid":
        pad_size = 0
        gshape = a.shape[0] - v.shape[0] + 1
    else:
        raise ValueError("Supported modes are 'full', 'valid', 'same', got {}".format(mode))

    a = pad(a, pad_size, "constant", 0)

    if a.is_distributed():
        if (v.lshape_map[:, 0] > a.lshape_map[:, 0]).any():
            raise ValueError("Local chunk of filter weight is larger than the local chunks of signal")
        # fetch halos and store them in a.halo_next/a.halo_prev
        a.get_halo(halo_size)
        # apply halos to local array
        signal = a.array_with_halos
    else:
        signal = a.larray

    # make signal and filter weight 3D for Pytorch conv1d function
    t_a = signal # stores temporary signal
    signal = signal.reshape(1, 1, signal.shape[0])
    
    # flip filter for convolution as Pytorch conv1d computes correlations
    v = flip(v, [0])
    if(v.larray.shape != v.lshape_map[0]):
        # pads weights if input kernel is uneven
        target = torch.zeros(v.lshape_map[0][0], dtype = v.larray.dtype)
        pad_size = v.lshape_map[0][0] - v.larray.shape[0]
        target[pad_size : ] = v.larray
        weight = target
    else: 
        weight = v.larray
    t_v = weight # stores temporary weight
    weight = weight.reshape(1, 1, weight.shape[0])

    # cast to float if on GPU
    if signal.is_cuda:
        float_type = promote_types(signal.dtype, torch.float32).torch_type()
        signal = signal.to(float_type)
        weight = weight.to(float_type)
   
    if v.comm.is_distributed() and a.split is not None and v.split is not None:
        rank = v.comm.rank
        size = v.comm.size

        t_signal_shape = (t_a.shape[0] - t_v.shape[0]) if(a.comm.rank != 0 and int(v.lshape_map[0][0] % 2) == 0) else (t_a.shape[0] - t_v.shape[0] + 1)
        t_signal = torch.zeros((v.comm.size, t_signal_shape))

        for r in range(size):
            dest_rank = r
            send = v.comm.Isend(t_v, dest_rank)
            send.Wait()
        for r in range(size):
            origin_rank = r
            recv = v.comm.Irecv(t_v, origin_rank)
            recv.Wait()

            t_v2 = t_v.reshape(1, 1, t_v.shape[0])
            local_signal_filtered = fc.conv1d(signal, t_v2)
            # unpack 3D result into 1D
            local_signal_filtered = local_signal_filtered[0, 0, :]

            if a.comm.rank != 0 and int(v.lshape_map[0][0] % 2) == 0:
                local_signal_filtered = local_signal_filtered[1:]
            t_signal[origin_rank] = local_signal_filtered

        global_signal_filtered = array(t_signal, dtype= t_signal.dtype, is_split= 1, device= a.device, comm= a.comm)
        signal_filtered = array(0)
        start_idx = 0
        for row in range(size):
            signal_filtered += global_signal_filtered[row][start_idx : start_idx + gshape]
            if(row != size-1): start_idx += int(v.lshape_map[row + 1][0])
        signal_filtered.balance_()
        return signal_filtered
    else:
        # apply torch convolution operator
        signal_filtered = fc.conv1d(signal, weight)

        # unpack 3D result into 1D
        signal_filtered = signal_filtered[0, 0, :] 

        # if kernel shape along split axis is even we need to get rid of duplicated values
        if a.comm.rank != 0 and v.shape[0] % 2 == 0:
            signal_filtered = signal_filtered[1:]

        return DNDarray(
            signal_filtered.contiguous(),
            (gshape,),
            signal_filtered.dtype,
            a.split,
            a.device,
            a.comm,
            balanced=False,
        ).astype(a.dtype.torch_type())
