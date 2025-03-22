from shared_atomic.atomic_object_backend cimport atomic_object
from libc.limits cimport ULLONG_MAX

cpdef size_t array_get_int(atomic_bytearray array) except ?ULLONG_MAX
cpdef bytes array_get_bytes(atomic_bytearray array, trim=*)
cpdef void array_set_bytes(atomic_bytearray array, bytes data) except*
cpdef bytes array_get_and_set(atomic_bytearray array, bytes data, bint trim=*)
cpdef bytes array_compare_and_set_value(atomic_bytearray array, bytes i , bytes n , bint trim=*)
cpdef void array_store(atomic_bytearray n, atomic_bytearray i) except*
cpdef void array_shift(atomic_bytearray n, atomic_bytearray i, atomic_bytearray j) except *
cpdef bint array_compare_and_set(atomic_bytearray j, atomic_bytearray i, bytes n) except *
cpdef bytes array_add_and_fetch(atomic_bytearray array, bytes n, bint trim=*)
cpdef bytes array_sub_and_fetch(atomic_bytearray array, bytes n, bint trim=*)
cpdef bytes array_and_and_fetch(atomic_bytearray array, bytes n, bint trim=*)
cpdef bytes array_or_and_fetch(atomic_bytearray array, bytes n, bint trim=*)
cpdef bytes array_xor_and_fetch(atomic_bytearray array, bytes n, bint trim=*)
cpdef bytes array_nand_and_fetch(atomic_bytearray array, bytes n, bint trim=*)
cpdef bytes array_fetch_and_add(atomic_bytearray array, bytes n, bint trim=*)
cpdef bytes array_fetch_and_sub(atomic_bytearray array, bytes n, bint trim=*)
cpdef bytes array_fetch_and_and(atomic_bytearray array, bytes n, bint trim=*)
cpdef bytes array_fetch_and_or(atomic_bytearray array, bytes n, bint trim=*)
cpdef bytes array_fetch_and_xor(atomic_bytearray array, bytes n, bint trim=*)
cpdef bytes array_fetch_and_nand(atomic_bytearray array, bytes n, bint trim=*)

cdef class atomic_bytearray(atomic_object):
    cdef signed char initial_length
    cpdef size_t get_int(self) except ?ULLONG_MAX
    cpdef bytes get_bytes(self, bint trim=*)
    cpdef void set_bytes(self, bytes data)
    cdef bytes _get_full_bytes(self)
    cpdef void array_store(self, atomic_bytearray i)
    cpdef bytes array_get_and_set(self, bytes data, bint trim=*)
    cpdef void array_shift(self, atomic_bytearray i, atomic_bytearray j)
    cpdef bint array_compare_and_set(self, atomic_bytearray i, bytes n)
    cpdef bytes array_compare_and_set_value(self, bytes i, bytes n, bint trim=*)
    cpdef bytes array_add_and_fetch(self, bytes n, bint trim=*)
    cpdef bytes array_sub_and_fetch(self, bytes n, bint trim=*)
    cpdef bytes array_and_and_fetch(self, bytes n, bint trim=*)
    cpdef bytes array_or_and_fetch(self, bytes n, bint trim=*)
    cpdef bytes array_xor_and_fetch(self, bytes n, bint trim=*)
    cpdef bytes array_nand_and_fetch(self, bytes n, bint trim=*)
    cpdef bytes array_fetch_and_add(self, bytes n, bint trim=*)
    cpdef bytes array_fetch_and_sub(self, bytes n, bint trim=*)
    cpdef bytes array_fetch_and_and(self, bytes n, bint trim=*)
    cpdef bytes array_fetch_and_or(self, bytes n, bint trim=*)
    cpdef bytes array_fetch_and_xor(self, bytes n, bint trim=*)
    cpdef bytes array_fetch_and_nand(self, bytes n, bint trim=*)
