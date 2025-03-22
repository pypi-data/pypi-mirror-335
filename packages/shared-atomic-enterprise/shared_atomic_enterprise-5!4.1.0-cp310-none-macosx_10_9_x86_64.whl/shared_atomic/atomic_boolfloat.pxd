from shared_atomic.atomic_object_backend cimport  atomic_object
from shared_atomic.atomic_object_backend cimport  DBL_MAX

cpdef bint bool_get(atomic_bool a ) except *
cpdef void bool_set(atomic_bool a, bint n) except *
cpdef void bool_store(atomic_bool a, atomic_bool b) except *
cpdef void bool_shift(atomic_bool a, atomic_bool b, atomic_bool n) except *
cpdef bint bool_get_and_set(atomic_bool a, bint n) except *
cpdef bint bool_compare_and_set(atomic_bool a, atomic_bool b, bint n) except *
cpdef bint bool_compare_and_set_value(atomic_bool a, bint e, bint n) except *

cdef class atomic_bool(atomic_object):
    cpdef bint get(self) except *
    cpdef void set(self, bint value) except*
    cpdef void bool_store(self, atomic_bool b) except *
    cpdef void bool_shift(self, atomic_bool b, atomic_bool c) except *
    cpdef bint bool_get_and_set(self, bint n) except *
    cpdef bint bool_compare_and_set(self, atomic_bool b, bint n) except *
    cpdef bint bool_compare_and_set_value(self, bint e, bint n) except *

cpdef double float_get(atomic_float a) except ?DBL_MAX
cpdef void float_set(atomic_float a, double n) except *
cpdef void float_store(atomic_float v, atomic_float n) except *

cdef class atomic_float(atomic_object):
    cpdef double get(self) except ?DBL_MAX
    cpdef void set(self, double value) except *
    cpdef void float_store(self, atomic_float n) except *