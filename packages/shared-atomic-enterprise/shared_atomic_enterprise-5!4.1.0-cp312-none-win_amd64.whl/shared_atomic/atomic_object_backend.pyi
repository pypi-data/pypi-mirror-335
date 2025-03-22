import _io
import shared_atomic as shared_atomic
from _typeshed import Incomplete
from typing import Any, ClassVar, Iterable

__pyx_capi__: dict
__test__: dict
activationlib_bytes: bytes
cpu_count: int
f: _io.BufferedReader

class array2d:
    buf: Incomplete
    def __init__(self, x: int, y: int, itemsize: int, signed: bool = ..., iterable: Iterable = ...) -> Any:
        """__init__(self, x: int, y: int, itemsize: int, signed: bool = True, iterable: Iterable = None)

        transform of unsigned integer to signed integer,

                :param x: first dimension
                :param y: second dimension
                :param itemsize: size of each integer element
                :param signed: whether the integer element is signed
                :param iterable: initializing value in Iterable object
                :return: array2d object
        """
    def __reduce__(self):
        """__reduce_cython__(self)"""

def atomic_object_remove(name: bytes) -> int:
    """atomic_object_remove(name: bytes) -> int

    deallocate the atomic_object except the shared_dict and atomic_shared_memory, which are based on file name.

         :param name: name of the atomic_object
         :return: 0 if successful
    """
