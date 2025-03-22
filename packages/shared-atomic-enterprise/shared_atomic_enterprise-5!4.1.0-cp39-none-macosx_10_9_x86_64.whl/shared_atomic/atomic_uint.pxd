from shared_atomic.atomic_object_backend cimport atomic_object
from libc.limits cimport ULLONG_MAX

cpdef size_t uint_get(atomic_uint integer) except? ULLONG_MAX
cpdef void uint_set(atomic_uint integer, size_t n) except *
cpdef size_t uint_get_and_set(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef void uint_store(atomic_uint integer, atomic_uint n) except *
cpdef void uint_shift(atomic_uint integer, atomic_uint n, atomic_uint r) except *
cpdef bint uint_compare_and_set(atomic_uint integer, atomic_uint e, size_t n) except *
cpdef size_t uint_compare_and_set_value(atomic_uint integer, size_t e, size_t n) except? ULLONG_MAX
cpdef size_t uint_add_and_fetch(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef size_t uint_sub_and_fetch(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef size_t uint_and_and_fetch(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef size_t uint_or_and_fetch(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef size_t uint_xor_and_fetch(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef size_t uint_nand_and_fetch(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef size_t uint_fetch_and_add(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef size_t uint_fetch_and_sub(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef size_t uint_fetch_and_and(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef size_t uint_fetch_and_or(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef size_t uint_fetch_and_xor(atomic_uint integer, size_t n) except? ULLONG_MAX
cpdef size_t uint_fetch_and_nand(atomic_uint integer, size_t n) except? ULLONG_MAX

cdef class atomic_uint(atomic_object):

    cpdef size_t get(self) except? ULLONG_MAX
    cpdef void set(self, size_t value) except *
    cpdef void uint_store(self, atomic_uint n) except *
    cpdef void uint_shift(self, atomic_uint n, atomic_uint r) except *
    cpdef size_t uint_and_and_fetch(self, size_t n) except? ULLONG_MAX
    cpdef size_t uint_or_and_fetch(self, size_t n) except? ULLONG_MAX
    cpdef size_t uint_xor_and_fetch(self, size_t n) except? ULLONG_MAX
    cpdef size_t uint_nand_and_fetch(self, size_t n) except? ULLONG_MAX
    cpdef size_t uint_get_and_set(self, size_t n) except? ULLONG_MAX
    cpdef bint uint_compare_and_set(self, atomic_uint e, size_t n) except *
    cpdef size_t uint_compare_and_set_value(self, size_t e,size_t n) except? ULLONG_MAX
    cpdef size_t uint_add_and_fetch(self, size_t n) except? ULLONG_MAX
    cpdef size_t uint_sub_and_fetch(self, size_t n) except? ULLONG_MAX
    cpdef size_t uint_fetch_and_add(self, size_t n) except? ULLONG_MAX
    cpdef size_t uint_fetch_and_sub(self, size_t n) except? ULLONG_MAX
    cpdef size_t uint_fetch_and_and(self, size_t n) except? ULLONG_MAX
    cpdef size_t uint_fetch_and_or(self,size_t n) except? ULLONG_MAX
    cpdef size_t uint_fetch_and_xor(self, size_t n) except? ULLONG_MAX
    cpdef size_t uint_fetch_and_nand(self, size_t n) except? ULLONG_MAX
