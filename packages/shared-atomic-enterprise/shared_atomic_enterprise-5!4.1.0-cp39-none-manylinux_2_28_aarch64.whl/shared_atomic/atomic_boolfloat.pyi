import _io
import shared_atomic as shared_atomic
import shared_atomic.atomic_object_backend
from typing import Any, ClassVar

__pyx_capi__: dict
__test__: dict
atomic_object_backend_bytes: bytes
f: _io.BufferedReader

class atomic_bool(shared_atomic.atomic_object_backend.atomic_object):
    __pyx_vtable__: ClassVar[PyCapsule] = ...
    value: value
    def __init__(self, name: bytes, value: bool = ...) -> Any:
        """__init__(self, name: bytes, value: bool = None)

        constructor of atomic_bool

            :param name: name of the shared variable with other instances
            :param value: initial value of atomic_bool
        """
    def bool_compare_and_set(self, b: atomic_bool, n: bool) -> bool:
        """bool_compare_and_set(self, b: atomic_bool, n: bool) -> bool

        Compare and set atomically. This compares the contents of self with the contents of b. If equal, the operation is a read-modify-write operation that writes n into self. If they are not equal, the operation is a read and the current contents of self are written into b.

                 :param b: atomic_bool object
                 :param n: the boolean value to set from
                 :return: the original boolean value
         """
    def bool_compare_and_set_value(self, e: bool, n: bool) -> bool:
        """bool_compare_and_set_value(self, e: bool, n: bool) -> bool

        Compare and set atomically. This compares the contents of self with the contents of n. If equal, the operation is a read-modify-write operation that writes n into self. If they are not equal, no operation will be taken. 

                    :param e: the  value to set from
                    :param n: the value to compare to
                    :return: None
        """
    def bool_get_and_set(self, n: bool) -> bool:
        """bool_get_and_set(self, n: bool) -> bool

        get and set atomically
            
                    :param n: value to set
                    :return: None
        """
    def bool_shift(self, b: atomic_bool, c: atomic_bool) -> void:
        """bool_shift(self, b: atomic_bool, c: atomic_bool) -> void

         value exchange between 3 atomic_bools in 2 groups atomically, store b in self after store self in c 

                 :param b: atomic_bool object
                 :param c: atomic_bool object
                 :return: None
         """
    def bool_store(self, b: atomic_bool) -> void:
        """bool_store(self, b: atomic_bool) -> void

        set the contents of atomic_bool object self atomically from another atomic_bool object b

                 :param b: atomic_bool object
                 :return: None
         """
    def get(self) -> bool:
        """get(self) -> bool

        get the bool value from the atomic_bool
                    :return: value
        """
    def set(self, value: bool) -> void:
        """set(self, value: bool) -> void

        set the bool value from the atomic_bool
                :param value: value to set
                :return: None
        """
    def __del__(self, *args, **kwargs) -> None: ...
    def __reduce__(self):
        """__reduce_cython__(self)"""

class atomic_float(shared_atomic.atomic_object_backend.atomic_object):
    __pyx_vtable__: ClassVar[PyCapsule] = ...
    value: value
    def __init__(self, name: bytes, value: float = ...) -> Any:
        """__init__(self, name: bytes, value: float = None)

        constructor of atomic_float

                :param value: initial value of atomic_float
                :param mode: 's' or 'singleprocessing' for single process, 'm' or 'multiprocessing' for multiprocessing
                :param windows_unix_compatibility: dummy parameter on unix platform, used on windows platform to indicate whether the source code should be compatible with unix platform
        """
    def float_store(self, n: atomic_float) -> void:
        """float_store(self, n: atomic_float) -> void

        set the contents of atomic_bool object self atomically from another atomic_float object n

                 :param n: atomic_float object
                 :return: None
         """
    def get(self) -> float:
        """get(self) -> float

        get the contents of atomic_float object atomically.
             
                    :return: the float value
        """
    def set(self, value: float) -> void:
        """set(self, value: float) -> void

        set the contents of atomic_float object atomically.

                 :param value: the float value to set from
                 :return: None
         """
    def __del__(self, *args, **kwargs) -> None: ...
    def __reduce__(self):
        """__reduce_cython__(self)"""

def __reduce_cython__(self) -> Any:
    """__reduce_cython__(self)"""
def __setstate_cython__(self, __pyx_state) -> Any:
    """__setstate_cython__(self, __pyx_state)"""
def bool_compare_and_set(a: atomic_bool, b: atomic_bool, n: bool) -> bool:
    """bool_compare_and_set(a: atomic_bool, b: atomic_bool, n: bool) -> bool

    Compare and set atomically. This compares the contents of a with the contents of b. If equal, the operation is a read-modify-write operation that writes n into self. If they are not equal, the operation is a read and the current contents of a are written into b.

         :param a: atomic_bool object
         :param b: atomic_bool object
         :param n: the boolean value to set from
         :return: the original boolean value
     """
def bool_compare_and_set_value(a: atomic_bool, e: bool, n: bool) -> bool:
    """bool_compare_and_set_value(a: atomic_bool, e: bool, n: bool) -> bool

    Compare and swap atomically, This compares the contents of atomic_bool object a with the contents of n. If equal, the operation is a read-modify-write operation that writes e into self. If they are not equal, No operation is performed.

         :param a: the atomic_bool object
         :param e: The exchange value
         :param n: the value to be compared with
         :return: the initial value
     """
def bool_get(boolean: atomic_bool) -> bool:
    """bool_get(boolean: atomic_bool) -> bool

    get the contents of atomic_bool object atomically.

         :param boolean: atomic_bool object
         :return: the boolean value
     """
def bool_get_and_set(a: atomic_bool, n: bool) -> bool:
    """bool_get_and_set(a: atomic_bool, n: bool) -> bool

    get and set contents of atomic_bool object atomically.

         :param a: atomic_bool object
         :param n: the boolean value to set from
         :return: the original boolean value
     """
def bool_set(boolean: atomic_bool, n: bool) -> void:
    """bool_set(boolean: atomic_bool, n: bool) -> void

    set the contents of atomic_bool object atomically.

         :param boolean: atomic_bool object
         :param n: the boolean value to set from
         :return: None
     """
def bool_shift(a: atomic_bool, b: atomic_bool, n: atomic_bool) -> void:
    """bool_shift(a: atomic_bool, b: atomic_bool, n: atomic_bool) -> void

     value exchange between 3 atomic_bools in 2 groups atomically, store b in a after store a in n 

         :param a: atomic_bool object
         :param b: atomic_bool object
         :param n: atomic_bool object
         :return: None
     """
def bool_store(a: atomic_bool, b: atomic_bool) -> void:
    """bool_store(a: atomic_bool, b: atomic_bool) -> void

    set the contents of atomic_bool object a atomically from another atomic_bool object b

         :param a: atomic_bool object
         :param b: atomic_bool object
         :return: None
     """
def float_get(a: atomic_float) -> float:
    """float_get(a: atomic_float) -> float

    get the contents of atomic_float object atomically.
            :return: the float value
    """
def float_set(a: atomic_float, n: float) -> void:
    """float_set(a: atomic_float, n: float) -> void

    set the contents of atomic_float object atomically.

         :param a: atomic_float object
         :param n: the float value to set from
         :return: None
     """
def float_store(v: atomic_float, n: atomic_float) -> void:
    """float_store(v: atomic_float, n: atomic_float) -> void

    set the contents of atomic_float object a atomically from another atomic_float object b

         :param v: atomic_float object
         :param n: atomic_float object
         :return: None
     """
