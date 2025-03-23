from typing import Optional
import io
import numpy as np
from h5py import *


class ExtendedFile(File):
    def __setitem__(self, name, obj):
        if isinstance(name, int):
            name = f'{name}'
        return super().__setitem__(name, obj)
    
    def __getitem__(self, name):
        if isinstance(name, int):
            name = f'{name}'
        return super().__getitem__(name)
    
    def __del__(self):
        self.close()


class ArrayFile:
    def __new__(cls, file, mode: str = 'r', mmap_mode: str = 'r'):
        if issubclass(type(file), io.IOBase):
            file = file.name
        if mmap_mode is not None:
            hdf5_file = File(file, 'r')
            arrays = {}
            def collect_datasets(name, item):
                if isinstance(item, Dataset):
                    offset = item.id.get_offset()
                    if offset is None:
                        raise ValueError(f"could not get the offset of the dataset '{name}', probably not a continuous array")
                    else:
                        arrays[name] = np.memmap(file, dtype=item.dtype, shape=item.shape, order='C', mode=mmap_mode, offset=offset)
            hdf5_file.visititems(collect_datasets)
            hdf5_file.close()
            return arrays
        else:
            return ExtendedFile(file, mode)


class LoadedFile:
    def __new__(cls, file):
        if issubclass(type(file), io.IOBase):
            file = file.name
        return ExtendedFile(file, 'r')


def save(
    path: str,
    *args,
    **kwargs
):
    with ExtendedFile(path, 'w') as file:
        for i, data in enumerate(args):
            file.create_dataset(f'{i}', data=data)
        for name, data in kwargs.items():
            file.create_dataset(name, data=data)


def load(path: str, mmap_mode: Optional[str] = None):
    if mmap_mode is None:
        return LoadedFile(path)
    else:
        return ArrayFile(path, 'r', mmap_mode)