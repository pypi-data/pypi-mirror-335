import contextlib
import struct
from collections.abc import Mapping
from io import BufferedWriter
from typing import Callable, Iterable, Sequence, Union, Optional
import numpy as np
from numpy.lib import format
from numpy.compat import os_fspath
from numpy._typing import DTypeLike
from sortedcontainers import SortedDict
from array_like_generic import *
from .utils.h5 import load as loadh5, save as saveh5
try:
    from scipy.special import gamma
finally: pass


class NpkFile(Mapping):
    def __init__(self, fid: BufferedWriter, keys, sizes, reader, mmap_mode):
        self.fid = fid
        self.reader = reader
        self.mmap_mode = mmap_mode
        self.sizes = SortedDict()
        for i, key in enumerate(keys):
            self.sizes.setdefault(key, sizes[i])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.fid.close()

    def __del__(self):
        self.close()

    # Implement the Mapping ABC
    def __iter__(self):
        return iter(self.sizes)

    def __len__(self):
        return len(self.sizes)
    
    def __get_from_key(self, key):
        self.fid.seek(self.sizes[key])
        return self.reader(self.fid, self.mmap_mode)

    def __getitem__(self, index):
        if isinstance(index, str):
            key = index
            return self.__get_from_key(key)
        else:
            key = index[0]
            return self.__get_from_key(key)[index[1:]]


def apply_from_axis(func: Callable, arr: np.ndarray, axis = 0, otypes: Iterable[DTypeLike] = None):
    '''
    Select an axis of an `numpy.ndarray` and apply a function.
    '''
    slices = (slice(None, None, None),) * (axis)
    if len(otypes) > 1:
        return tuple(np.array(item, dtype=otypes[i]) for i, item in enumerate(zip(*[func(arr[slices + (i,)]) for i in range(arr.shape[axis])])))
    elif len(otypes) == 1:
        return np.array([func(arr[slices + (i,)]) for i in range(arr.shape[axis])], otypes[0], copy=False)
    else:
        [func(arr[slices + (i,)]) for i in range(arr.shape[axis])]


def map_range(
    array: np.ndarray,
    interval: Sequence[int] = (0, 1),
    axis: Union[int, Sequence[int], None] = None,
    dtype: np.dtype = None,
    scalar_default: ScalarDefault = ScalarDefault.max,
    eps: float = 1e-6
):
    min_value: np.ndarray = np.min(array, axis=axis, keepdim=True)
    max_value: np.ndarray = np.max(array, axis=axis, keepdim=True)
    max_min_difference = max_value - min_value
    max_min_equal_mask = max_min_difference == 0
    max_min_difference[max_min_equal_mask] = 1
    array = array - min_value
    array[np.broadcast_to(max_min_equal_mask, array.shape)] = np.asarray(scalar_default_value(scalar_default, eps)).astype(array.dtype)
    return (array / max_min_difference * (interval[1] - interval[0]) + interval[0]).astype(dtype)


def map_ranges(
    array: np.ndarray,
    intervals: Sequence[Sequence[int]] = [(0, 1)],
    axis: Union[int, Sequence[int], None] = None,
    dtype: Optional[np.dtype] = None,
    scalar_default: ScalarDefault = ScalarDefault.max,
    eps: float = 1.e-6
):
    min_value: np.ndarray = np.min(array, dims=axis, keepdims=True)
    max_value: np.ndarray = np.max(array, dims=axis, keepdims=True)
    max_min_difference = max_value - min_value
    max_min_equal_mask = max_min_difference == 0
    max_min_difference[max_min_equal_mask] = 1
    normed = (array - min_value) / max_min_difference
    normed[np.broadcast_to(max_min_equal_mask, array.shape)] = np.asarray(scalar_default_value(scalar_default, eps)).astype(array.dtype)
    def generator():
        for interval in intervals:
            yield (normed * (interval[1] - interval[0]) + interval[0]).astype(dtype)
    return tuple(*generator())


def linspace_at(index, start, stop, num):
    common_difference = np.array((stop - start) / (num - 1), copy=False)
    index = np.array(index, copy=False)
    return start + common_difference * index.reshape([*index.shape] + [1] * len(common_difference.shape))


def linspace_cumprod_at(index, start, stop, num):
    start = np.array(start, copy=False)
    stop = np.array(stop, copy=False)
    common_difference = (stop - start) / (num - 1)
    index = np.array(index, copy=False)
    result_index_prefix = (slice(None),) * len(index.shape)
    n = index + 1
    n_shape = n.shape
    result = np.zeros((*n.shape, *common_difference.shape))
    zero_common_difference_mask = common_difference == 0
    left_required_shape, right_required_shape = broadcast_required_shape(start[zero_common_difference_mask].shape, n_shape)
    n = n.reshape(right_required_shape)
    result[combine_mask_index(result_index_prefix, zero_common_difference_mask)] = np.power(start[zero_common_difference_mask].reshape(left_required_shape), n)
    sequence_with_zero_mask = np.zeros_like(zero_common_difference_mask)
    nonzero_common_difference_mask = common_difference != 0
    sequence_with_zero_mask[nonzero_common_difference_mask] = (start[nonzero_common_difference_mask]) % common_difference[nonzero_common_difference_mask] == 0
    sequence_with_zero_mask[nonzero_common_difference_mask] &= (np.sign(start[nonzero_common_difference_mask]) != np.sign(common_difference[nonzero_common_difference_mask]))
    del nonzero_common_difference_mask
    result[combine_mask_index(result_index_prefix, sequence_with_zero_mask)] = 0
    first_divided_mask = np.logical_not(sequence_with_zero_mask | zero_common_difference_mask)
    del zero_common_difference_mask
    del sequence_with_zero_mask
    first_divided = np.full(common_difference.shape, np.nan)
    first_divided[first_divided_mask] = start[first_divided_mask] / common_difference[first_divided_mask]
    first_divided_gt_eq_zero_mask = first_divided > 0
    left_required_shape, right_required_shape = broadcast_required_shape(common_difference[first_divided_gt_eq_zero_mask].shape, n_shape)
    n = n.reshape(right_required_shape)
    result[combine_mask_index(result_index_prefix, first_divided_gt_eq_zero_mask)] = np.power(common_difference[first_divided_gt_eq_zero_mask].reshape(left_required_shape), n) * gamma(first_divided[first_divided_gt_eq_zero_mask].reshape(left_required_shape) + n) / gamma(first_divided[first_divided_gt_eq_zero_mask].reshape(left_required_shape))
    del first_divided_gt_eq_zero_mask
    first_divided_lt_zero_mask = first_divided < 0
    left_required_shape, right_required_shape = broadcast_required_shape(common_difference[first_divided_lt_zero_mask].shape, n_shape)
    n = n.reshape(right_required_shape)
    result[combine_mask_index(result_index_prefix, first_divided_lt_zero_mask)] = np.power(-common_difference[first_divided_lt_zero_mask].reshape(left_required_shape), n) * gamma(-first_divided[first_divided_lt_zero_mask].reshape(left_required_shape) + 1) / gamma(-first_divided[first_divided_lt_zero_mask].reshape(left_required_shape) - n + 1)
    return result


def savek(file, **kwds):
    if hasattr(file, 'write'):
        file_ctx = contextlib.nullcontext(file)
    else:
        file = os_fspath(file)
        if not file.endswith('.npk'):
            file = file + '.npk'
        file_ctx = open(file, "wb")

    keys = np.array([key for key in kwds])
    sizes = np.empty(len(keys) + 1, dtype=int)
    
    with file_ctx as fid:
        for i, (_, arr) in enumerate(kwds.items()):
            sizes[i] = fid.tell()
            arr = np.asanyarray(arr)
            format.write_array(fid, arr, allow_pickle=True,
                            pickle_kwargs=None)
        sizes[-1] = fid.tell()
        format.write_array(fid, keys, allow_pickle=True,
                        pickle_kwargs=None)
        sizes_tell = fid.tell()
        format.write_array(fid, sizes, allow_pickle=True,
                        pickle_kwargs=None)
        fid.write(struct.pack('I', sizes_tell))


def loadk(file, mmap_mode=None,
         encoding='ASCII', *, max_header_size=format._MAX_HEADER_SIZE):
    if encoding not in ('ASCII', 'latin1', 'bytes'):
        raise ValueError("encoding must be 'ASCII', 'latin1', or 'bytes'")

    if hasattr(file, 'read'):
        fid = file
    else:
        fid = open(os_fspath(file), "rb")
    
    def read_numpy(fid, mmap_mode):
        N = len(format.MAGIC_PREFIX)
        magic = fid.read(N)
        # If the file size is less than N, we need to make sure not
        # to seek past the beginning of the file
        fid.seek(-min(N, len(magic)), 1)  # back-up
        if magic == format.MAGIC_PREFIX:
            if mmap_mode:
                version = format.read_magic(fid)
                shape, fortran_order, dtype = format._read_array_header(
                        fid, version, max_header_size=max_header_size)
                if dtype.hasobject:
                    msg = "Array can't be memory-mapped: Python objects in dtype."
                    raise ValueError(msg)
                offset = fid.tell()
                if fortran_order:
                    order = 'F'
                else:
                    order = 'C'
                return np.memmap(fid, dtype=dtype, shape=shape, order=order,
                        mode=mmap_mode, offset=offset)
            else:
                return format.read_array(fid, allow_pickle=True,
                                        pickle_kwargs=None,
                                        max_header_size=max_header_size)
    
    int_size = struct.calcsize('I')
    fid.seek(-int_size, 2)
    sizes_tell = struct.unpack('I', fid.read(int_size))[0]
    fid.seek(sizes_tell)
    sizes = read_numpy(fid, False)
    fid.seek(sizes[-1])
    keys = read_numpy(fid, False)
    sizes = sizes[:-1]
    
    return NpkFile(fid, keys, sizes, read_numpy, mmap_mode)


# def map_range(arr: np.ndarray, range: Sequence[int] = (0, 1), axis: Optional[int] = None, dtype = None, scalar_default = ScalarDefault.max):
#     assert range[0] < range[1]
#     min_value = np.min(arr, axis, keepdims=True)
#     max_value = np.max(arr, axis, keepdims=True)
#     result = np.empty(arr.shape, dtype=dtype)
#     unrangable_index = np.where(max_value == min_value)[0]
#     if len(unrangable_index) > 0:
#         result[unrangable_index] = scalar_default_value(scalar_default, range)
#     rangable_index = np.where(max_value != min_value)[0]
#     if len(rangable_index) > 0:
#         rangable_min = min_value[rangable_index]
#         result[rangable_index] = (arr[rangable_index] - rangable_min) / (max_value[rangable_index] - rangable_min) * (range[1] - range[0]) + range[0]
#     return result


# def map_ranges(arr: np.ndarray, ranges: Sequence[int] = [(0, 1)], axis: Optional[int] = None, dtype=None, scalar_default = ScalarDefault.max):
#     min_value = np.min(arr, axis, keepdims=True)
#     max_value = np.max(arr, axis, keepdims=True)
#     unrangable_index = np.where(max_value == min_value)[0]
#     rangable_index = np.where(max_value != min_value)[0]
#     results = np.empty(len(ranges), dtype=object)
#     rangable_min = min_value[rangable_index]
#     normed = (arr[rangable_index] - rangable_min) / (max_value[rangable_index] - rangable_min)
#     del rangable_min
#     for i, range in enumerate(ranges):
#         assert range[0] < range[1]
#         results[i] = np.empty(arr.shape, dtype=dtype)
#         if len(unrangable_index) > 0:
#             results[i][unrangable_index] = scalar_default_value(scalar_default, range)
#         if len(rangable_index) > 0:
#             results[i][rangable_index] = normed * (range[1] - range[0]) + range[0]
#     return results


def permute(array: np.ndarray, axes: Sequence[int]):
    return np.transpose(array, axes)


def full_transpose(arr: np.ndarray):
    return np.transpose(arr, np.arange(len(arr.shape))[::-1])