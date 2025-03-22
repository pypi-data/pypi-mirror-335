import _io
import shared_atomic as shared_atomic
from _typeshed import Incomplete
from typing import Any, ClassVar

__pyx_capi__: dict
__test__: dict
atomic_object_backend_bytes: bytes
f: _io.BufferedReader

class shared_dict:
    __pyx_vtable__: ClassVar[PyCapsule] = ...
    file_name: Incomplete
    def __init__(self, name: bytes = ..., size: int = ..., bucket_chunk_size_exponent: int = ..., bucket_chunk_number: int = ..., chunk_size_exponent: int = ...) -> Any:
        """__init__(self, name: bytes = None, size: int = 650000000, bucket_chunk_size_exponent: int = 20, bucket_chunk_number: int = 100, chunk_size_exponent: int = 5)

        constructor of shared_dict

                :param name: file name of the shared dict
                :param size: file size of the shared dict
                :param bucket_chunk_size_exponent: the exponent of the hash bucket chunk size in the base of 2, for example, 20 means the the hash bucket chunk size is 2**20=1048576.
                :param bucket_chunk_number: the number of the hash bucket chunks, for example, 100 means there are 100 hash bucket chunks; the size of each of them is determined by the previous parameter bucket_chunk_size_exponent.
                :param chunk_size_exponent: the exponent of the data chunk size when allocating from shared memory in the base of 2, for example, 5 means the the data chunk size is 2**5=32 bytes when allocating from shared memory.
        """
    def expansion(self, parallelism: int = ...) -> int:
        """expansion(self, parallelism: int = 0) -> int

        expand the shared_dict in parallel

                :param parallelism: the degree of parallelism, if 0, it is the number of logical CPUs the calling thread is restricted to, same as os.cpu_count().
                :return: 1 if successfully expanded
        """
    def get(self, input_key) -> list:
        """get(self, input_key) -> list

        get the target object from shared_dict with input_key
    
                :param input_key: the target key value
                :return: list in form of [Boolean, object]. The first boolean value indicates whether the input_key is in the dict. The second python object is the target object if the first boolean value is True. 
        """
    def insert(self, input_key, input_value) -> int:
        """insert(self, input_key, input_value) -> int

        insert the shared_dict with input_key and input_value

                :param input_key: the target key value
                :param input_value: python object to insert 
                :return: 1 if successful
        """
    def remove(self, input_key) -> int:
        """remove(self, input_key) -> int

        remove the target object from shared_dict with input_key

                :param input_key: the target key value
                :return: 1 if successfully removed, 0 if the input_key not in the target shared_dict
        """
    def __del__(self, *args, **kwargs) -> None: ...
    def __len__(self) -> int:
        """Return len(self)."""
    def __reduce__(self):
        """__reduce_cython__(self)"""

def __reduce_cython__(self) -> Any:
    """__reduce_cython__(self)"""
def __setstate_cython__(self, __pyx_state) -> Any:
    """__setstate_cython__(self, __pyx_state)"""
def dict_get(target: shared_dict, input_key) -> list:
    """dict_get(target: shared_dict, input_key) -> list

    get the target object from shared_dict with input_key

        :param target: the target shared_dict
        :param input_key: the target key value
        :return: list in form of [Boolean, object]. The first boolean value indicates whether the input_key is in the dict. The second python object is the target object if the first boolean value is True. 
    """
def dict_insert(target: shared_dict, input_key, input_value) -> int:
    """dict_insert(target: shared_dict, input_key, input_value) -> int

    insert the target shared_dict with input_key and input_value

        :param target: the target shared_dict
        :param input_key: the target key value
        :param input_value: python object to insert 
        :return: 1 if successful
    """
def dict_remove(target: shared_dict, input_key) -> int:
    """dict_remove(target: shared_dict, input_key) -> int

    remove the target object from shared_dict with input_key

        :param target: the target shared_dict
        :param input_key: the target key value
        :return: 1 if successfully removed, 0 if the input_key not in the target shared_dict
    """
