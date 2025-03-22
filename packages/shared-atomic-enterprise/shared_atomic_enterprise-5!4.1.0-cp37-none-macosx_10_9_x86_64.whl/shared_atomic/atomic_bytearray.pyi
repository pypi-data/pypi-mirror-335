import _io
import shared_atomic as shared_atomic
import shared_atomic.atomic_object_backend
from typing import Any, ClassVar

__pyx_capi__: dict
__test__: dict
atomic_object_backend_bytes: bytes
f: _io.BufferedReader

class atomic_bytearray(shared_atomic.atomic_object_backend.atomic_object):
    __pyx_vtable__: ClassVar[PyCapsule] = ...
    int_value: int_value
    value: value
    def __init__(self, name: bytes, initial: bytes = ..., length: int = ..., paddingdirection: unicode = ..., paddingbytes: bytes = ..., trimming_direction: unicode = ...) -> Any:
        """__init__(self, name: bytes, initial: bytes = None, length: int = None, paddingdirection: unicode = u'right', paddingbytes: bytes = b'\\x00', trimming_direction: unicode = u'right')

        constructor to initialize the string,
                the string should be no longer than 8 bytes

                :param initial: initial value of the string, if the initial value is longer than 8 bytes, please specify the trimming target length, or else it would fail.
                :param mode: the mode in which the string will be shared. 'singleprocessing' or 's' for single process, 'multiprocessing' or 'm' for multiprocessing, on windows platform, only singleprocessing is supported, setting it to 'm' or 'multiprocessing' will be ignored.
                :param length: the expected length after padding/trimming for the input value, if not specified, no padding or trimming performed, use original value.
                :param paddingdirection: right, or left side the padding bytes would be added if not specified, pad to the right side, use 'right' or 'r' to specify right side, use 'left' or 'l' to specify the left side.
                :param paddingbytes: bytes to pad to the original bytes, by default '\\0' can be multiple bytes like b'ab', will be padded to the original bytes in circulation until the expected length is reached.
                :param trimming_direction: if initial bytes are longer, on which side the bytes will be trimmed. By default, on the right side, use 'right' or 'r' to specify right side, use 'left' or 'l' to specify the left side.
                :param windows_unix_compatibility: dummy parameter on unix platform, used on windows platform to indicate whether the source code should be compatible with unix platform
        """
    def array_add_and_fetch(self, n: bytes, trim: bool = ...) -> bytes:
        """array_add_and_fetch(self, n: bytes, trim: bool = True) -> bytes

        Increment and fetch atomically

                :param n: bytes will be added to the array.
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True
                :return: the contents of resulted bytearray
        """
    def array_and_and_fetch(self, n: bytes, trim: bool = ...) -> bytes:
        """array_and_and_fetch(self, n: bytes, trim: bool = True) -> bytes

        bitwise AND and fetch the result atomically

                :param n: the other operand of AND operation.
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True
                :return: the contents of resulted bytearray
        """
    def array_compare_and_set(self, i: atomic_bytearray, n: bytes) -> bool:
        """array_compare_and_set(self, i: atomic_bytearray, n: bytes) -> bool

        Compare and set atomically,This compares the contents of self with the contents of i. If equal, the operation is a read-modify-write operation that writes n into self. If they are not equal, the operation is a read and the current contents of itself are written into i.

                :param i: the bytearray to be compared with
                :return: if self is equal to i return True, else return False
        """
    def array_compare_and_set_value(self, i: bytes, n: bytes, trim: bool = ...) -> bytes:
        """array_compare_and_set_value(self, i: bytes, n: bytes, trim: bool = True) -> bytes

        Compare and swap atomically, This compares the contents of self
                with the contents of n. If equal, the operation is a read-modify-write
                operation that writes n into self. If they are not equal,
                No operation will be performed.

                :param i: exchange value
                :param n: The value to be compared with
                :param trim: whether the returned bytes should be trimmed of tailing b'\\0'
                :return: the initial value of the self
        """
    def array_fetch_and_add(self, n: bytes, trim: bool = ...) -> bytes:
        """array_fetch_and_add(self, n: bytes, trim: bool = True) -> bytes

        fetch and increment atomically

                :param n: the bytes will be added to the array
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True

                :return: the original contents of the bytearray
        """
    def array_fetch_and_and(self, n: bytes, trim: bool = ...) -> bytes:
        """array_fetch_and_and(self, n: bytes, trim: bool = True) -> bytes

        Fetch then bitwise AND atomically

                :param n: the other operands of AND operation
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True
                :return: the original contents of the bytearray
        """
    def array_fetch_and_nand(self, n: bytes, trim: bool = ...) -> bytes:
        """array_fetch_and_nand(self, n: bytes, trim: bool = True) -> bytes

        Fetch then bitwise NAND atomically

                :param n: the other operands of NAND operation
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True
                :return: the original contents of the bytearray
        """
    def array_fetch_and_or(self, n: bytes, trim: bool = ...) -> bytes:
        """array_fetch_and_or(self, n: bytes, trim: bool = True) -> bytes

        Fetch then bitwise OR atomically

                :param n: the other operands of OR operation
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True
                :return: the original contents of the bytearray
        """
    def array_fetch_and_sub(self, n: bytes, trim: bool = ...) -> bytes:
        """array_fetch_and_sub(self, n: bytes, trim: bool = True) -> bytes

        fetch and decrement atomically

                :param n: the bytes will be substracted from the array
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True
                :return: the original contents of the bytearray
        """
    def array_fetch_and_xor(self, n: bytes, trim: bool = ...) -> bytes:
        """array_fetch_and_xor(self, n: bytes, trim: bool = True) -> bytes

        Fetch then bitwise XOR atomically

                :param n: the other operands of XOR operation
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True
                :return: the original contents of the bytearray
        """
    def array_get_and_set(self, data: bytes, trim: bool = ...) -> bytes:
        """array_get_and_set(self, data: bytes, trim: bool = True) -> bytes

        Get and set atomically

                :param data: new data
                :param trim: whether of not to trim the returning b'\\0' when get, default True

                :return: the original bytes
        """
    def array_nand_and_fetch(self, n: bytes, trim: bool = ...) -> bytes:
        """array_nand_and_fetch(self, n: bytes, trim: bool = True) -> bytes

        bitsise NAND and fetch the result atomically

                :param n: the other operand of NAND operation
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True
                :return: the contents of resulted bytearray
        """
    def array_or_and_fetch(self, n: bytes, trim: bool = ...) -> bytes:
        """array_or_and_fetch(self, n: bytes, trim: bool = True) -> bytes

        bitsise OR and fetch the result atomically

                :param n: the other operand of OR operation
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True
                :return: the contents of resulted bytearray
        """
    def array_shift(self, i: atomic_bytearray, j: atomic_bytearray) -> void:
        """array_shift(self, i: atomic_bytearray, j: atomic_bytearray) -> void

        Value exchange between 3 bytearrays in 2 groups atomically,
                the initial_length field will be updated but not atomically.
                store i in itself after store itself in j

                :param i: one atomic_bytearray
                :param j: another atomic_bytearray
                :return: None
        """
    def array_store(self, i: atomic_bytearray) -> void:
        """array_store(self, i: atomic_bytearray) -> void

        Atomically store contents from another bytearray to this bytearray,
                if the other bytearray is different with this one in size , the function will fail.

                :param i: another bytearray to store its value to self
                :return: None
        """
    def array_sub_and_fetch(self, n: bytes, trim: bool = ...) -> bytes:
        """array_sub_and_fetch(self, n: bytes, trim: bool = True) -> bytes

        Decrement and fetch atomically

                :param n: bytes will be subtracted from the array.
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True
                :return: the contents of resulted bytearray
        """
    def array_xor_and_fetch(self, n: bytes, trim: bool = ...) -> bytes:
        """array_xor_and_fetch(self, n: bytes, trim: bool = True) -> bytes

        bitsise XOR and fetch the result atomically

                :param n: the other operand of XOR operation
                :param trim: whether of not to trim the returning b'\\0' when fetch, default True
                :return: the contents of resulted bytearray
        """
    def get_bytes(self, trim: bool = ...) -> bytes:
        """get_bytes(self, trim: bool = True) -> bytes

        Get all the bytes from the bytearray atomically
            
                    :param trim: if True, the leading b'\\0' would be trimmed, by default: True
                    :return: all the bytes in the bytearray
            """
    def get_int(self) -> int:
        """get_int(self) -> int

        Get the integer representation from the bytearray,
                    the whole array would be treated as a large integer

                    :return: the integer representation
            """
    def set_bytes(self, data: bytes) -> void:
        """set_bytes(self, data: bytes) -> void

        Set the value in the bytearray,
                    if the new data is longer than the original size of the array.
                    it will expand the array accordingly which would lose atomicy.
                    the size of the bytearray can be check with self.size

                    :param data: input bytearray
                    :return: None
            """
    def __del__(self, *args, **kwargs) -> None: ...
    def __reduce__(self):
        """__reduce_cython__(self)"""

def __reduce_cython__(self) -> Any:
    """__reduce_cython__(self)"""
def __setstate_cython__(self, __pyx_state) -> Any:
    """__setstate_cython__(self, __pyx_state)"""
def array_add_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_add_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    Increment and fetch atomically

            :param array: target array to change.
            :param n: bytes will be added to the array.
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the contents of resulted bytearray
        """
def array_and_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_and_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    Bitwise and and then fetch atomically

            :param array: target array to change.
            :param n: the other operands of AND operation
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the original contents of the bytearray
        """
def array_compare_and_set(j: atomic_bytearray, i: atomic_bytearray, data: bytes) -> bool:
    """array_compare_and_set(j: atomic_bytearray, i: atomic_bytearray, data: bytes) -> bool


            Compare and set atomically, this compares the contents of j with the contents of i. If equal, the operation is a read-modify-write operation that writes n into self. If they are not equal, the operation is a read and the current contents of j are written into i.
        
            :param i: the string to compare
            :param j: the string to be compared with
            :param data: another bytes to be ready to self if comparision return True
            :return: if self is equal to i return True, else return False
        """
def array_compare_and_set_value(array: atomic_bytearray, i: bytes, n: bytes, trim: bool = ...) -> bytes:
    """array_compare_and_set_value(array: atomic_bytearray, i: bytes, n: bytes, trim: bool = True) -> bytes

    Compare and set atomically,This compares the contents of self
        with the contents of i. If equal, the operation is a read-modify-write
        operation that writes n into self. If they are not equal,
        the operation is a read and the current contents of itself are written into i.

        :param array: target array to change.
        :param i: The exchange value
        :param n: The value to compare to
        :param trim: whether the returned bytes should be trimmed of tailing b'\\0'
        :return: Original value
    """
def array_fetch_and_add(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_fetch_and_add(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    fetch and increment atomically

            :param array: target array to change.
            :param n: the bytes will be added to the array
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the original contents of the bytearray
        """
def array_fetch_and_and(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_fetch_and_and(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    Fetch then bitwise AND atomically

            :param array: target array to change.
            :param n: the other operands of AND operation
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the original contents of the bytearray
        """
def array_fetch_and_nand(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_fetch_and_nand(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    Fetch then bitwise NAND atomically

            :param array: target array to change.
            :param n: the other operands of XOR operation
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the original contents of the bytearray
        """
def array_fetch_and_or(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_fetch_and_or(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    Fetch then bitwise OR atomically

            :param array: target array to change.
            :param n: the other operands of OR operation
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the original contents of the bytearray
        """
def array_fetch_and_sub(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_fetch_and_sub(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    fetch and decrement atomically

            :param array: target array to change.
            :param n: the bytes will be substracted from the array
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the original contents of the bytearray
        """
def array_fetch_and_xor(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_fetch_and_xor(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    Fetch then bitwise XOR atomically

            :param array: target array to change.
            :param n: the other operands of XOR operation
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the original contents of the bytearray
        """
def array_get_and_set(array: atomic_bytearray, data: bytes, trim: bool = ...) -> bytes:
    """array_get_and_set(array: atomic_bytearray, data: bytes, trim: bool = True) -> bytes

    Get and set atomically

        :param array: target array to change.
        :param data: new data
        :param trim: if True, the leading b'\\0' would be trimmed, by default: True
        :return: the original bytes
    """
def array_get_bytes(array: atomic_bytearray, trim=...) -> bytes:
    """array_get_bytes(array: atomic_bytearray, trim=True) -> bytes

    Get all the bytes from the bytearray atomically

        :param array: target array.
        :param trim: if True, the leading b'\\0' would be trimmed, by default: True

        :return: all the bytes in the bytearray
    """
def array_get_int(array: atomic_bytearray) -> int:
    """array_get_int(array: atomic_bytearray) -> int

    Get the integer representation from the bytearray,
        the whole array would be treated as a large integer
    
        :param array: target array.
        :return: the integer representation
    """
def array_nand_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_nand_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    Bitwise nand and then fetch atomically

            :param array: target array to change.
            :param n: the other operands of XOR operation
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the original contents of the bytearray
        """
def array_or_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_or_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    Bitwise or and then fetch atomically

            :param array: target array to change.
            :param n: the other operands of OR operation
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the original contents of the bytearray
        """
def array_set_bytes(array: atomic_bytearray, data: bytes) -> void:
    """array_set_bytes(array: atomic_bytearray, data: bytes) -> void

    Set the bytes for the bytearray,

        :param array: target array.
        :param data: bytes to set the data.
        :return: None
    """
def array_shift(n: atomic_bytearray, i: atomic_bytearray, j: atomic_bytearray) -> void:
    """array_shift(n: atomic_bytearray, i: atomic_bytearray, j: atomic_bytearray) -> void

    Value exchange between 3 pointers in 2 groups atomically,
            the initial_length field will be updated but not atomically.
            store i in n after store n in j

            :param n: one atomic_string
            :param i: one atomic_string
            :param j: another atomic_string
            :return: None
        """
def array_store(n: atomic_bytearray, i: atomic_bytearray) -> void:
    """array_store(n: atomic_bytearray, i: atomic_bytearray) -> void

    Set the bytes for the bytearray from another bytearray,
        :param n: target array.
        :param i: source array.
        :return: None
    """
def array_sub_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_sub_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    Decrement and fetch atomically
            :param array: target array to change.
            :param n: bytes will be subtracted from the array.
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the contents of resulted bytearray
        """
def array_xor_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = ...) -> bytes:
    """array_xor_and_fetch(array: atomic_bytearray, n: bytes, trim: bool = True) -> bytes

    Bitwise xor and then fetch atomically

            :param array: target array to change.
            :param n: the other operands of XOR operation
            :param trim: whether of not to trim the returning b'\\0' when fetch, default True
            :return: the original contents of the bytearray
        """
