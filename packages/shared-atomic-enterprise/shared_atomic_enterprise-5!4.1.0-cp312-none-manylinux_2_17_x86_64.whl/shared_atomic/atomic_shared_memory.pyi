import _io
import shared_atomic as shared_atomic
import shared_atomic.atomic_object_backend
from _typeshed import Incomplete
from typing import Any, ClassVar

__pyx_capi__: dict
__test__: dict
atomic_object_backend_bytes: bytes
cpu_count: int
f: _io.BufferedReader

class atomic_shared_memory(shared_atomic.atomic_object_backend.atomic_object):
    __pyx_vtable__: ClassVar[PyCapsule] = ...
    buf: Incomplete
    dealloc_async: dealloc_async
    def __init__(self, initial: bytes = ..., length: int = ..., paddingdirection: unicode = ..., paddingbytes: bytes = ..., trimming_direction: unicode = ..., source: unicode = ..., previous_shared_memory_path: unicode = ..., remove_previous_file: bool = ..., dealloc_async: bool = ...) -> Any:
        """__init__(self, initial: bytes = b'\\x00', length: int = None, paddingdirection: unicode = None, paddingbytes: bytes = b'\\x00', trimming_direction: unicode = u'right', source: unicode = u'p', previous_shared_memory_path: unicode = None, remove_previous_file: bool = False, dealloc_async: bool = False)

        constructor to initialize the shared memory

                :param initial: initial value in the shared memory.
                :param length: the expected length after padding/trimming for the input value, if not specified, no padding or trimming performed, use original value.
                :param paddingdirection: if not specified, no padding is performed, if specified, right, or left side the padding bytes would be added, use 'right' or 'r' to specify right side, use 'left' or 'l' to specify the left side.
                :param paddingbytes: bytes to pad to the original bytes, by default b'\\0' can be multiple bytes like b'ab', will be padded to the original bytes in circulation until the expected length is reached.
                :param trimming_direction: if initial bytes are longer, on which side the bytes will be trimmed. By default, on the right side, use 'right' or 'r' to specify right side, use 'left' or 'l' to specify the left side.
                :param source: if the data source is file, use 'f', if the data source is the initial parameter, let it remain default 'p'.
                :param previous_shared_memory_path: if the data source is file, set the path of the file
                :param remove_previous_file: if the data source is file, whether the data file should be deleted after initialization
                :param dealloc_async: whether the deallocation run in asynchronized fashion, useless on Microsoft Windows platform.
        """
    def file_sync(self, _async: bool = ..., start: int = ..., length: int = ...) -> int:
        """file_sync(self, async: bool = False, start: int = 0, length: int = 0) -> int

        sync to the file system for standalone shared memory

                :param async: whether the file writes are synchronized on unix platform, True for asynchronize, False for synchronize. Useless on windows platform, which is always synchronized
                :param start: starting offset of the shared memory to sync.
                :param length: length of bytes in the shared memory to sync.
                :return: 0 if sucessful, raises exception otherwise.
        """
    def memdump(self, file_path: unicode, start: int = ..., length: int = ...) -> int:
        """memdump(self, file_path: unicode, start: int = 0, length: int = 0) -> int

        Dump the data at specific offset given specific length using memcpy, it's NOT atomic method
                the data can be any length.

                :param file_path: file path the dump of the shared memory is written to
                :param start: offset in the shared memory from which the data is dumped
                :param length: the length of data in bytes to dump
                :return: number of bytes written to disk
        """
    def offset_add_and_fetch(self, value: bytes, offset: int = ...) -> bytes:
        """offset_add_and_fetch(self, value: bytes, offset: int = 0) -> bytes

        increment and fetch atomically

                :param value: data to add
                :param offset: the offset inside the shared memory starting from 0 you need to add,
                :return: sum of the 2 values
        """
    def offset_add_and_fetches(self, *args, **kwargs):
        """offset_add_and_fetches(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        increment and fetch atomically at specific offsets given specific lengths

                :param values: rows of bytes to add to, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of sum of the two bytes representation of values and shared memory bytes, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_and_and_fetch(self, value: bytes, offset: int = ...) -> bytes:
        """offset_and_and_fetch(self, value: bytes, offset: int = 0) -> bytes

        bitwise AND and fetch the result atomically

                :param value: data to AND
                :param offset: the offset inside the shared memory starting from 0 you need to AND with,
                :return: the result value
        """
    def offset_and_and_fetches(self, *args, **kwargs):
        """offset_and_and_fetches(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        Bitwise AND and fetch atomically at specific offsets given specific lengths

                :param values: rows of bytes to AND, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of differences of the two bytes representation of values and shared memory bytes, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_compare_and_set(self, shared_memory2: atomic_shared_memory, value: bytes, offset: int = ..., offset2: int = ...) -> bool:
        """offset_compare_and_set(self, shared_memory2: atomic_shared_memory, value: bytes, offset: int = 0, offset2: int = 0) -> bool

        Compare and set atomically. This compares the contents of shared_memory2 at offset2 with the contents of self at offset. If equal, the operation is a read-modify-write operation that writes bytes parameter value into self. If they are not equal, the operation is a read and the current contents of self are written into shared_memory2.

                :param shared_memory2: the other shared memory from which the data is from
                :param value: the value to write to the shared memory,
                :param offset: the offset inside the shared memory starting from 0 you need to set,
                :param offset2: the offset2 inside the shared memory 2 starting from 0 you need to get,
                :return: whether the contents of self and contents of shared_memory2 is the same
        """
    def offset_compare_and_set_value(self, i: bytes, n: bytes, offset: int = ...) -> bytes:
        """offset_compare_and_set_value(self, i: bytes, n: bytes, offset: int = 0) -> bytes

        Compare and set atomically. This compares the contents of n with the contents of self at offset. If equal, the operation is a read-modify-write operation that writes bytes parameter value into self. If they are not equal, no operation will be taken.
        
                :param i: exchange value
                :param n: The value to be compared with
                :param offset: the offset inside the shared memory starting from 0 you need to set,
                :return: the original value at offset
        """
    def offset_compare_and_set_values(self, *args, **kwargs):
        """offset_compare_and_set_values(self, ies: const_char[:,_:], ns: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        Atomically get and set the bytes at specific offsets given specific lengths

                :param ies: rows of bytes to set from, each row will be right trimmed according to the lengths array
                :param ns: rows of bytes to be compared with, each row will be right trimmed according to the lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of original bytes at specific offsets, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_compare_and_sets(self, other_memories: list, values, offsets, offsets2, lengths, parallelism: int = ...) -> list:
        """offset_compare_and_sets(self, other_memories: list, values: const_char[:,_:], offsets: const_size_t[:], offsets2: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> list

        Compare and set atomically. This compares the contents of shared_memory2 at offset2 with the contents of self at offset. If equal, the operation is a read-modify-write operation that writes bytes parameter value into self. If they are not equal, the operation is a read and the current contents of self are written into shared_memory2.

                :param other_memories: the other shared memorys from which the data is from
                :param values: the value to write to the shared memory,
                :param offsets: the offset inside the shared memory starting from 0 you need to set,
                :param offsets2: the offset2 inside the shared memory 2 starting from 0 you need to get,
                :param lengths: the length to compare and set,
                :return: whether the contents of self and contents of shared_memory2 is the same
        """
    def offset_compare_with_other_type_and_set(self, object2: atomic_object, value: bytes, offset: int = ...) -> bool:
        """offset_compare_with_other_type_and_set(self, object2: atomic_object, value: bytes, offset: int = 0) -> bool

        Compare and set atomically. This compares the contents of another atomic_object with the contents of self at offset. 
                If equal, the operation is a read-modify-write operation that writes bytes parameter value into self. 
                If they are not equal, the operation is a read and the current contents of self are written into object2.

                :param object2: the other atomic object from which the data is compared with
                :param offset: the offset inside the shared memory starting from 0 you need to compare and set,
                :param value: value to be set
                :return: whether the contents of self and contents of object2 is the same
        """
    def offset_fetch_and_add(self, value: bytes, offset: int = ...) -> bytes:
        """offset_fetch_and_add(self, value: bytes, offset: int = 0) -> bytes

        fetch and increment atomically

                :param value: data to add
                :param offset: the offset inside the shared memory starting from 0 you need to add to,
                :return: original value
        """
    def offset_fetch_and_adds(self, *args, **kwargs):
        """offset_fetch_and_adds(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        fetch and increment atomically at specific offsets given specific lengths

                :param values: rows of bytes to add to, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of original bytes representation of  shared memory, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_fetch_and_and(self, value: bytes, offset: int = ...) -> bytes:
        """offset_fetch_and_and(self, value: bytes, offset: int = 0) -> bytes

        fetch then bitwise AND atomically

                :param value: value to AND to
                :param offset: the offset inside the shared memory starting from 0 you need to AND to,
                :return: original value
        """
    def offset_fetch_and_ands(self, *args, **kwargs):
        """offset_fetch_and_ands(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        fetch and AND atomically at specific offsets given specific lengths

                :param values: rows of bytes to and, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of original bytes representation of  shared memory, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_fetch_and_nand(self, value: bytes, offset: int = ...) -> bytes:
        """offset_fetch_and_nand(self, value: bytes, offset: int = 0) -> bytes

        fetch then bitwise NAND atomically

                :param value: value to NAND with
                :param offset: the offset inside the shared memory starting from 0 you need to NAND with,
                :return: original value
        """
    def offset_fetch_and_nands(self, *args, **kwargs):
        """offset_fetch_and_nands(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        fetch and NAND atomically at specific offsets given specific lengths

                :param values: rows of bytes to xor, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of original bytes representation of  shared memory, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_fetch_and_or(self, value: bytes, offset: int = ...) -> bytes:
        """offset_fetch_and_or(self, value: bytes, offset: int = 0) -> bytes

        fetch then bitwise OR atomically

                :param value: value to OR with
                :param offset: the offset inside the shared memory starting from 0 you need to OR with,
                :return: original value
        """
    def offset_fetch_and_ors(self, *args, **kwargs):
        """offset_fetch_and_ors(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        fetch and OR atomically at specific offsets given specific lengths

                :param values: rows of bytes to or, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of original bytes representation of  shared memory, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_fetch_and_sub(self, value: bytes, offset: int = ...) -> bytes:
        """offset_fetch_and_sub(self, value: bytes, offset: int = 0) -> bytes

        fetch and substract atomically

                :param value: data to add
                :param offset: the offset inside the shared memory starting from 0 you need to substract from,
                :return: original value
        """
    def offset_fetch_and_subs(self, *args, **kwargs):
        """offset_fetch_and_subs(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        fetch and substract atomically at specific offsets given specific lengths

                :param values: rows of bytes to substract, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of original bytes representation of  shared memory, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_fetch_and_xor(self, value: bytes, offset: int = ...) -> bytes:
        """offset_fetch_and_xor(self, value: bytes, offset: int = 0) -> bytes

        fetch then bitwise XOR atomically

                :param value: value to XOR with
                :param offset: the offset inside the shared memory starting from 0 you need to XOR with,
                :return: original value
        """
    def offset_fetch_and_xors(self, *args, **kwargs):
        """offset_fetch_and_xors(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        fetch and XOR atomically at specific offsets given specific lengths

                :param values: rows of bytes to xor, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of original bytes representation of  shared memory, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_get(self, offset: int = ..., length: int = ...) -> bytes:
        """offset_get(self, offset: int = 0, length: int = 1) -> bytes

        Atomically get the bytes at specific offset given specific length

                :param offset: the offset inside the shared memory starting from 0, including the operation length
                :param length: the length of bytes should be retrieved
                :return: bytes at specific offset.
        """
    def offset_get_and_set(self, value: bytes, offset: int = ...) -> bytes:
        """offset_get_and_set(self, value: bytes, offset: int = 0) -> bytes

        Atomically set the bytes at specific offset given specific length

                :param value: new value in bytes
                :param offset: the offset inside the shared memory starting from 0, including the operation length
                :return: bytes at specific offset previously.
        """
    def offset_get_and_sets(self, *args, **kwargs):
        """offset_get_and_sets(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        Atomically get the bytes at specific offsets given specific lengths

                :param values: rows of bytes at specific offsets, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of bytes at specific offsets, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_gets(self, *args, **kwargs):
        """offset_gets(self, offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        Atomically get the bytes at specific offsets given specific lengths

                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of bytes at specific offsets, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_memmove(self, mv: object, offset: int = ..., io_flags: unicode = ...) -> void:
        """offset_memmove(self, mv: object, offset: int = 0, io_flags: unicode = u'i') -> void

        Set or read the data at specific offset given specific length using memcpy, it's NOT atomic method
                the data can be any length incase you don't need atomicity or should use other lengths

                :param mv: the data source as memoryview to read from or write to
                :param offset: offset in the shared memory to read from or write to
                :param io_flags: 'i' to write from the mv to the shared memory, 'o' to read from the shared memory to the mv
                :return: None
        """
    def offset_nand_and_fetch(self, value: bytes, offset: int = ...) -> bytes:
        """offset_nand_and_fetch(self, value: bytes, offset: int = 0) -> bytes

        bitwise NAND and fetch the result atomically

                :param value: data to NAND
                :param offset: the offset inside the shared memory starting from 0 you need to NAND with,
                :return: the result value
        """
    def offset_nand_and_fetches(self, *args, **kwargs):
        """offset_nand_and_fetches(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        Bitwise NAND and fetch atomically at specific offsets given specific lengths

                :param values: rows of bytes to NAND, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of differences of the two bytes representation of values and shared memory bytes, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_or_and_fetch(self, value: bytes, offset: int = ...) -> bytes:
        """offset_or_and_fetch(self, value: bytes, offset: int = 0) -> bytes

        bitwise OR and fetch the result atomically
        
                :param value: data to OR
                :param offset: the offset inside the shared memory starting from 0 you need to OR with,
                :return: the result value
        """
    def offset_or_and_fetches(self, *args, **kwargs):
        """offset_or_and_fetches(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        Bitwise OR and fetch atomically at specific offsets given specific lengths

                :param values: rows of bytes to OR, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of differences of the two bytes representation of values and shared memory bytes, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_store(self, shared_memory2: atomic_shared_memory, offset: int = ..., offset2: int = ..., length: int = ...) -> void:
        """offset_store(self, shared_memory2: atomic_shared_memory, offset: int = 0, offset2: int = 0, length: int = 1) -> void

        Atomically set the data at specific offset given specific length

                :param shared_memory2: the other shared memory from which the data is from
                :param offset: the offset inside the shared memory starting from 0 you need to set,
                :param offset2: the offset inside the shared memory from the data you want,
                :param length: the length of bytes should be set in the shared memory and get the data from the shared memory 2, only 1,2,4 and 8 are supported
                :return: None
        """
    def offset_store_from_other_types(self, object2: atomic_object, offset: int = ...) -> void:
        """offset_store_from_other_types(self, object2: atomic_object, offset: int = 0) -> void

        Atomically set the data at specific offset given specific length, 
                if object2 is in variable length, and object2 is changing the size at the same time, 
                the method will not be atomic, otherwise, the operation is atomic.

                :param object2: the other atomic object from which the data is from
                :param offset: the offset inside the shared memory starting from 0 you need to set
                :return: None
        """
    def offset_stores(self, other_memories: list, offsets, offsets2, lengths, parallelism: int = ...) -> void:
        """offset_stores(self, other_memories: list, offsets: size_t[:], offsets2: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> void"""
    def offset_stores_from_other_types(self, other_objects: list, offsets, parallelism: int = ...) -> void:
        """offset_stores_from_other_types(self, other_objects: list, offsets: const_size_t[:], parallelism: int = 0) -> void"""
    def offset_sub_and_fetch(self, value: bytes, offset: int = ...) -> bytes:
        """offset_sub_and_fetch(self, value: bytes, offset: int = 0) -> bytes

        increment and fetch atomically

                :param value: data to add
                :param offset: the offset inside the shared memory starting from 0 you need to add,
                :return: sum of the 2 values
        """
    def offset_sub_and_fetches(self, *args, **kwargs):
        """offset_sub_and_fetches(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        substract and fetch atomically at specific offsets given specific lengths

                :param values: rows of bytes to substract, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of differences of the two bytes representation of values and shared memory bytes, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def offset_xor_and_fetch(self, value: bytes, offset: int = ...) -> bytes:
        """offset_xor_and_fetch(self, value: bytes, offset: int = 0) -> bytes

        bitwise XOR and fetch the result atomically

                :param value: data to XOR
                :param offset: the offset inside the shared memory starting from 0 you need to XOR with,
                :return: the result value
        """
    def offset_xor_and_fetches(self, *args, **kwargs):
        """offset_xor_and_fetches(self, values: const_char[:,_:], offsets: const_size_t[:], lengths: const_char[:], parallelism: int = 0) -> char[:,_::1]

        Bitwise XOR and fetch atomically at specific offsets given specific lengths

                :param values: rows of bytes to XOR, rows will be right trimmed according to lengths array
                :param offsets: the array of offsets inside the shared memory starting from 0
                :param lengths: the array of lengths of bytes should be retrieved
                :param parallelism: the wanted degree of parallelism
                :return: rows of differences of the two bytes representation of values and shared memory bytes, the width is the max given length, rows of other lengths are padded by '\\0'.
        """
    def __del__(self, *args, **kwargs) -> None: ...
    def __reduce__(self):
        """__reduce_cython__(self)"""

def __reduce_cython__(self) -> Any:
    """__reduce_cython__(self)"""
def __setstate_cython__(self, __pyx_state) -> Any:
    """__setstate_cython__(self, __pyx_state)"""
def shared_memory_offset_add_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_add_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    increment and fetch atomically

        :param memory: target shared memory
        :param value: data to add
        :param offset: the offset inside the shared memory starting from 0 you need to add,
        :return: sum of the 2 values
    """
def shared_memory_offset_and_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_and_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    bitwise AND and fetch the result atomically

        :param memory: target shared memory
        :param value: data to AND
        :param offset: the offset inside the shared memory starting from 0 you need to AND with,
        :return: the result value
    """
def shared_memory_offset_compare_and_set(memory: atomic_shared_memory, shared_memory2: atomic_shared_memory, value: bytes, offset: int = ..., offset2: int = ...) -> bool:
    """shared_memory_offset_compare_and_set(memory: atomic_shared_memory, shared_memory2: atomic_shared_memory, value: bytes, offset: int = 0, offset2: int = 0) -> bool

    Compare and set atomically. This compares the contents of shared_memory2 at offset2 with the contents of memory at offset. If equal, the operation is a read-modify-write operation that writes bytes parameter value into self. If they are not equal, the operation is a read and the current contents of memory are written into shared_memory2.

        :param memory: target shared memory
        :param shared_memory2: the other shared memory from which the data is from
        :param value: the value to write to the shared memory,
        :param offset: the offset inside the shared memory starting from 0 you need to set,
        :param offset2: the offset2 inside the shared memory 2 starting from 0 you need to get,
        :return: whether the contents of memory and contents of shared_memory2 is the same
    """
def shared_memory_offset_compare_and_set_value(memory: atomic_shared_memory, i: bytes, n: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_compare_and_set_value(memory: atomic_shared_memory, i: bytes, n: bytes, offset: int = 0) -> bytes

    Compare and set atomically. This compares the contents of n with the contents of memory at offset. If equal, the operation is a read-modify-write operation that writes bytes parameter value into memory. If they are not equal, no operation will be taken.

        :param memory: target shared memory
        :param i: exchange value
        :param n: The value to be compared with
        :param offset: the offset inside the shared memory starting from 0 you need to set,
        :return: the original value at offset
    """
def shared_memory_offset_compare_with_other_type_and_set(memory: atomic_shared_memory, object2: atomic_object, value: bytes, offset: int = ...) -> bool:
    """shared_memory_offset_compare_with_other_type_and_set(memory: atomic_shared_memory, object2: atomic_object, value: bytes, offset: int = 0) -> bool

    Compare and set atomically. This compares the contents of another  atomic_object with the contents of memory at offset. If equal, the operation is a read-modify-write operation that writes bytes parameter value into memory. If they are not equal, the operation is a read and the current contents of self are written into object2.

        :param memory: target shared memory
        :param object2: the other atomic object from which the data is compared with
        :param offset: the offset inside the shared memory starting from 0 you need to compare and set,
        :param value: value to be set
        :return: whether the contents of memory and contents of object2 is the same
    """
def shared_memory_offset_fetch_and_add(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_fetch_and_add(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    fetch and increment atomically

        :param value: data to add
        :param offset: the offset inside the shared memory starting from 0 you need to add to,
        :return: original value
    """
def shared_memory_offset_fetch_and_and(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_fetch_and_and(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    fetch then bitwise AND atomically

        :param value: value to AND to
        :param offset: the offset inside the shared memory starting from 0 you need to AND to,
        :return: original value
    """
def shared_memory_offset_fetch_and_nand(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_fetch_and_nand(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    fetch then bitwise NAND atomically

        :param value: value to NAND with
        :param offset: the offset inside the shared memory starting from 0 you need to NAND with,
        :return: original value
    """
def shared_memory_offset_fetch_and_or(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_fetch_and_or(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    fetch then bitwise OR atomically

        :param value: value to OR with
        :param offset: the offset inside the shared memory starting from 0 you need to OR with,
        :return: original value
    """
def shared_memory_offset_fetch_and_sub(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_fetch_and_sub(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    fetch and substract atomically

        :param value: data to sub
        :param offset: the offset inside the shared memory starting from 0 you need to substract from,
        :return: original value
    """
def shared_memory_offset_fetch_and_xor(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_fetch_and_xor(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    fetch then bitwise XOR atomically

        :param value: value to XOR with
        :param offset: the offset inside the shared memory starting from 0 you need to XOR with,
        :return: original value
    """
def shared_memory_offset_get(memory: atomic_shared_memory, offset: int = ..., length: int = ...) -> bytes:
    """shared_memory_offset_get(memory: atomic_shared_memory, offset: int = 0, length: int = 1) -> bytes

    Atomically get the bytes at specific offset given specific length

        :param memory: target shared memory
        :param offset: the offset inside the shared memory starting from 0
        :param length: the length of bytes should be retrieved
        :return: bytes at specific offset.
    """
def shared_memory_offset_get_and_set(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_get_and_set(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    Atomically set the bytes at specific offset given specific length

        :param memory: target shared memory
        :param value: new value in bytes
        :param offset: the offset inside the shared memory starting from 0, including the operation length
        :return: bytes at specific offset previously.
    """
def shared_memory_offset_nand_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_nand_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    bitwise NAND and fetch the result atomically

        :param value: data to NAND
        :param offset: the offset inside the shared memory starting from 0 you need to NAND with,
        :return: the result value
    """
def shared_memory_offset_or_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_or_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    bitwise OR and fetch the result atomically
    
        :param value: data to OR
        :param offset: the offset inside the shared memory starting from 0 you need to OR with,
        :return: the result value
    """
def shared_memory_offset_store(memory: atomic_shared_memory, shared_memory2: atomic_shared_memory, offset: int = ..., offset2: int = ..., length: int = ...) -> void:
    """shared_memory_offset_store(memory: atomic_shared_memory, shared_memory2: atomic_shared_memory, offset: int = 0, offset2: int = 0, length: int = 1) -> void

    Atomically set the data at specific offset given specific length

        :param memory: target shared memory
        :param shared_memory2: the other shared memory from which the data is from
        :param offset: the offset inside the shared memory starting from 0 you need to set,
        :param offset2: the offset inside the shared memory from the data you want,
        :param length: the length of bytes should be set in the shared memory and get the data from the shared memory 2, only 1,2,4 and 8 are supported
        :return: None
    """
def shared_memory_offset_store_from_other_types(memory: atomic_shared_memory, object2: atomic_object, offset: int = ...) -> void:
    """shared_memory_offset_store_from_other_types(memory: atomic_shared_memory, object2: atomic_object, offset: int = 0) -> void

    Atomically set the data at specific offset given specific length, 
        if object2 is in variable length, and object2 is changing the size at the same time, 
        the method will not be atomic, otherwise, the operation is atomic.

        :param memory: target shared memory
        :param object2: the other atomic object from which the data is from
        :param offset: the offset inside the shared memory starting from 0 you need to set
        :return: None
    """
def shared_memory_offset_sub_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_sub_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    increment and fetch atomically

        :param memory: target shared memory
        :param value: data to sub
        :param offset: the offset inside the shared memory starting from 0 you need to add,
        :return: sum of the 2 values
    """
def shared_memory_offset_xor_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = ...) -> bytes:
    """shared_memory_offset_xor_and_fetch(memory: atomic_shared_memory, value: bytes, offset: int = 0) -> bytes

    bitwise XOR and fetch the result atomically

        :param value: data to XOR
        :param offset: the offset inside the shared memory starting from 0 you need to XOR with,
        :return: the result value
    """

