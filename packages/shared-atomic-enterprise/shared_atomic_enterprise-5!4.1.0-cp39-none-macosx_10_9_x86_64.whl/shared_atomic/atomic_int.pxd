from shared_atomic.atomic_object_backend cimport atomic_object
from libc.limits cimport LLONG_MAX

cpdef Py_ssize_t int_get(atomic_int integer) except? LLONG_MAX
cpdef void int_set(atomic_int integer, Py_ssize_t n) except *
cpdef Py_ssize_t int_get_and_set(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef void int_store(atomic_int integer, atomic_int n) except *
cpdef void int_shift(atomic_int integer, atomic_int n, atomic_int r) except *
cpdef bint int_compare_and_set(atomic_int integer, atomic_int e, Py_ssize_t n) except *
cpdef Py_ssize_t int_compare_and_set_value(atomic_int integer, Py_ssize_t e, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_add_and_fetch(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_sub_and_fetch(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_and_and_fetch(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_or_and_fetch(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_xor_and_fetch(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_nand_and_fetch(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_fetch_and_add(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_fetch_and_sub(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_fetch_and_and(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_fetch_and_or(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_fetch_and_xor(atomic_int integer, Py_ssize_t n) except? LLONG_MAX
cpdef Py_ssize_t int_fetch_and_nand(atomic_int integer, Py_ssize_t n) except? LLONG_MAX

cdef class atomic_int(atomic_object):

    cpdef Py_ssize_t get(self) except? LLONG_MAX
    cpdef void set(self, Py_ssize_t value) except *
    cpdef void int_store(self, atomic_int n) except *
    cpdef void int_shift(self, atomic_int n, atomic_int r) except *
    cpdef Py_ssize_t int_and_and_fetch(self, Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_or_and_fetch(self, Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_xor_and_fetch(self, Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_nand_and_fetch(self, Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_get_and_set(self, Py_ssize_t n) except? LLONG_MAX
    cpdef bint int_compare_and_set(self, atomic_int e, Py_ssize_t n) except *
    cpdef Py_ssize_t int_compare_and_set_value(self, Py_ssize_t e,Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_add_and_fetch(self, Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_sub_and_fetch(self, Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_fetch_and_add(self, Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_fetch_and_sub(self, Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_fetch_and_and(self, Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_fetch_and_or(self,Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_fetch_and_xor(self, Py_ssize_t n) except? LLONG_MAX
    cpdef Py_ssize_t int_fetch_and_nand(self, Py_ssize_t n) except? LLONG_MAX
