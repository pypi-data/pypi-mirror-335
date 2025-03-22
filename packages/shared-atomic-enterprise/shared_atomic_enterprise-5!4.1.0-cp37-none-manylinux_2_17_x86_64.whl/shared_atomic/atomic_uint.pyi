import _io
import shared_atomic as shared_atomic
import shared_atomic.atomic_object_backend
from typing import Any, ClassVar

__pyx_capi__: dict
__test__: dict
atomic_object_backend_bytes: bytes
f: _io.BufferedReader

class atomic_uint(shared_atomic.atomic_object_backend.atomic_object):
    __pyx_vtable__: ClassVar[PyCapsule] = ...
    value: value
    def __init__(self, name: bytes, value: int = ...) -> Any:
        """__init__(self, name: bytes, value: int = None)

        constructor of atomic_int

                :param value: read/write value of the integer

                :param name: name of the shared variable with other instances

        """
    def get(self) -> int:
        """get(self) -> int

        get the contents of atomic_uint atomically.

                 :return: the int value
         """
    def set(self, value: int) -> void:
        """set(self, value: int) -> void

        set the contents of atomic_uint atomically.

                 :param value: the integer value to set from
                 :return: None
         """
    def uint_add_and_fetch(self, n: int) -> int:
        """uint_add_and_fetch(self, n: int) -> int

        increment and fetch atomically

                :param n: data to add
                :return: sum of the 2 values
        """
    def uint_and_and_fetch(self, n: int) -> int:
        """uint_and_and_fetch(self, n: int) -> int

        bitwise AND and fetch the result atomically

                :param n: data to AND
                :return: the result value
        """
    def uint_compare_and_set(self, e: atomic_uint, n: int) -> bool:
        """uint_compare_and_set(self, e: atomic_uint, n: int) -> bool

        Compare and set atomically. This compares the contents of self with the contents of e. If equal, the operation is a read-modify-write operation that writes n into self. If they are not equal, the operation is a read and the current contents of self are written into e.

                 :param e: atomic_uint object
                 :param n: the integer value to set from
                 :return: if self is equal to e return True, else return False
         """
    def uint_compare_and_set_value(self, e: int, n: int) -> int:
        """uint_compare_and_set_value(self, e: int, n: int) -> int

        Compare and set atomically. This compares the contents of self with the contents of n. If equal, the operation is a read-modify-write operation that writes e into self. If they are not equal, no operation will be taken.

                :param e: The exchange value
                :param n: The value to compare to
                :return: initial value
        """
    def uint_fetch_and_add(self, n: int) -> int:
        """uint_fetch_and_add(self, n: int) -> int

        fetch and increment atomically

                :param n: data to add
                :return: original value
        """
    def uint_fetch_and_and(self, n: int) -> int:
        """uint_fetch_and_and(self, n: int) -> int

        fetch then bitwise AND atomically

                :param n: data to AND
                :return: original value
        """
    def uint_fetch_and_nand(self, n: int) -> int:
        """uint_fetch_and_nand(self, n: int) -> int

        fetch then bitwise NAND atomically

                :param n: data to NAND
                :return: original value
        """
    def uint_fetch_and_or(self, n: int) -> int:
        """uint_fetch_and_or(self, n: int) -> int

        fetch then bitwise OR atomically

                :param n: data to OR
                :return: original value
        """
    def uint_fetch_and_sub(self, n: int) -> int:
        """uint_fetch_and_sub(self, n: int) -> int

        fetch and subtract atomically

                :param n: data to subtract
                :return: original value
        """
    def uint_fetch_and_xor(self, n: int) -> int:
        """uint_fetch_and_xor(self, n: int) -> int

        fetch then bitwise XOR atomically

                :param n: data to XOR
                :return: original value
        """
    def uint_get_and_set(self, n: int) -> int:
        """uint_get_and_set(self, n: int) -> int

        get and set contents of atomic_uint atomically.

                 :param n: the integer value to set from
                 :return: the original int value
         """
    def uint_nand_and_fetch(self, n: int) -> int:
        """uint_nand_and_fetch(self, n: int) -> int

        bitwise NAND and fetch the result atomically

                :param n: data to NAND
                :return: the result value
        """
    def uint_or_and_fetch(self, n: int) -> int:
        """uint_or_and_fetch(self, n: int) -> int

        bitwise XOR and fetch the result atomically

                :param n: data to OR
                :return: the result value
        """
    def uint_shift(self, n: atomic_uint, r: atomic_uint) -> void:
        """uint_shift(self, n: atomic_uint, r: atomic_uint) -> void

        value exchange between 3 atomic_uints in 2 groups atomically, store n in self after store self in r.

                 :param n: the atomic_uint n
                 :param r: the atomic_uint r
                 :return: None
         """
    def uint_store(self, n: atomic_uint) -> void:
        """uint_store(self, n: atomic_uint) -> void

        Store value atomically.

                 :param n: the atomic_uint to set from
                 :return: None
         """
    def uint_sub_and_fetch(self, n: int) -> int:
        """uint_sub_and_fetch(self, n: int) -> int

        sub and fetch atomically

                :param n: data to subtract
                :return: difference of the 2 values
        """
    def uint_xor_and_fetch(self, n: int) -> int:
        """uint_xor_and_fetch(self, n: int) -> int

        bitwise XOR and fetch the result atomically

                :param n: data to XOR
                :return: the result value
        """
    def __del__(self, *args, **kwargs) -> None: ...
    def __reduce__(self):
        """__reduce_cython__(self)"""

def __reduce_cython__(self) -> Any:
    """__reduce_cython__(self)"""
def __setstate_cython__(self, __pyx_state) -> Any:
    """__setstate_cython__(self, __pyx_state)"""
def uint_add_and_fetch(integer: atomic_uint, n: int) -> int:
    """uint_add_and_fetch(integer: atomic_uint, n: int) -> int

    increment and fetch atomically

        :param integer: the atomic_uint
        :param n: the integer value
        :return: sum of the 2 values
    """
def uint_and_and_fetch(integer: atomic_uint, n: int) -> int:
    """uint_and_and_fetch(integer: atomic_uint, n: int) -> int

    Bitwise AND and fetch atomically

        :param integer: the atomic_uint
        :param n: data to AND
        :return: the result value
    """
def uint_compare_and_set(integer: atomic_uint, e: atomic_uint, n: int) -> bool:
    """uint_compare_and_set(integer: atomic_uint, e: atomic_uint, n: int) -> bool

    Compare and set atomically. This compares the contents of integer with the contents of e. If equal, the operation is a read-modify-write operation that writes n into integer. If they are not equal, the operation is a read and the current contents of integer are written into e.

         :param integer: atomic_uint object
         :param e: atomic_uint object
         :param n: the integer value to set from
         :return: if integer is equal to e return True, else return False
     """
def uint_compare_and_set_value(integer: atomic_uint, e: int, n: int) -> int:
    """uint_compare_and_set_value(integer: atomic_uint, e: int, n: int) -> int

    Compare and swap atomically, This compares the contents of atomic_uint integer with the contents of n. If equal, the operation is a read-modify-write operation that writes e into integer. If they are not equal, No operation is performed.

         :param integer: the atomic_uint
         :param e: the integer value
         :param n: the integer value
         :return: the initial value
     """
def uint_fetch_and_add(integer: atomic_uint, n: int) -> int:
    """uint_fetch_and_add(integer: atomic_uint, n: int) -> int

    increment and fetch atomically

        :param integer: the atomic_uint
        :param n: data to add
        :return: the initial value
    """
def uint_fetch_and_and(integer: atomic_uint, n: int) -> int:
    """uint_fetch_and_and(integer: atomic_uint, n: int) -> int

    fetch then bitwise AND atomically

        :param integer: the atomic_uint
        :param n: data to AND
        :return: the initial value
    """
def uint_fetch_and_nand(integer: atomic_uint, n: int) -> int:
    """uint_fetch_and_nand(integer: atomic_uint, n: int) -> int

    fetch then bitwise NAND atomically

        :param integer: the atomic_uint
        :param n: data to NAND
        :return: the initial value
    """
def uint_fetch_and_or(integer: atomic_uint, n: int) -> int:
    """uint_fetch_and_or(integer: atomic_uint, n: int) -> int

    fetch then bitwise OR atomically

        :param integer: the atomic_uint
        :param n: data to OR
        :return: the initial value
    """
def uint_fetch_and_sub(integer: atomic_uint, n: int) -> int:
    """uint_fetch_and_sub(integer: atomic_uint, n: int) -> int

    subtract and fetch atomically

        :param integer: the atomic_uint
        :param n: data to subtract
        :return: the initial value
    """
def uint_fetch_and_xor(integer: atomic_uint, n: int) -> int:
    """uint_fetch_and_xor(integer: atomic_uint, n: int) -> int

    fetch then bitwise XOR atomically

        :param integer: the atomic_uint
        :param n: data to XOR
        :return: the initial value
    """
def uint_get(integer: atomic_uint) -> int:
    """uint_get(integer: atomic_uint) -> int

    get the contents of atomic_uint atomically.

         :param integer: the atomic_uint to get
         :return: the int value
     """
def uint_get_and_set(integer: atomic_uint, n: int) -> int:
    """uint_get_and_set(integer: atomic_uint, n: int) -> int

    get and set contents of atomic_uint atomically.

         :param integer: the atomic_uint
         :param n: the integer value to set from
         :return: the original int value
     """
def uint_nand_and_fetch(integer: atomic_uint, n: int) -> int:
    """uint_nand_and_fetch(integer: atomic_uint, n: int) -> int

    Bitwise NAND and fetch atomically

        :param integer: the atomic_uint
        :param n: data to NAND
        :return: the result value
    """
def uint_or_and_fetch(integer: atomic_uint, n: int) -> int:
    """uint_or_and_fetch(integer: atomic_uint, n: int) -> int

    Bitwise OR and fetch atomically

        :param integer: the atomic_uint
        :param n: data to OR
        :return: the result value
    """
def uint_set(integer: atomic_uint, n: int) -> void:
    """uint_set(integer: atomic_uint, n: int) -> void

    set the contents of atomic_uint atomically.

         :param integer: the atomic_uint to set
         :param n: the integer value to set from
         :return: None
     """
def uint_shift(integer: atomic_uint, n: atomic_uint, r: atomic_uint) -> void:
    """uint_shift(integer: atomic_uint, n: atomic_uint, r: atomic_uint) -> void

    value exchange between 3 atomic_uint in 2 groups atomically, store n in integer after store integer in r.

         :param integer: the atomic_uint integer
         :param n: the atomic_uint n
         :param r: the atomic_uint r
         :return: None
     """
def uint_store(integer: atomic_uint, n: atomic_uint) -> void:
    """uint_store(integer: atomic_uint, n: atomic_uint) -> void

    Store value atomically.

         :param integer: the atomic_uint to set
         :param n: the atomic_uint to set from
         :return: None
     """
def uint_sub_and_fetch(integer: atomic_uint, n: int) -> int:
    """uint_sub_and_fetch(integer: atomic_uint, n: int) -> int

    sub and fetch atomically

        :param integer: the atomic_uint
        :param n: the integer value
        :return: sum of the 2 values
    """
def uint_xor_and_fetch(integer: atomic_uint, n: int) -> int:
    """uint_xor_and_fetch(integer: atomic_uint, n: int) -> int

    Bitwise XOR and fetch atomically

        :param integer: the atomic_uint
        :param n: data to XOR
        :return: the result value
    """
