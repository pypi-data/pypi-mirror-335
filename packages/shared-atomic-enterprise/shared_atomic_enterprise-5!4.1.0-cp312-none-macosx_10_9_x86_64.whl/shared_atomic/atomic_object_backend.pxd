cdef extern from "<float.h>" nogil:
    const double DBL_MAX

cpdef int atomic_object_remove(bytes name) except -1

cdef class atomic_object:
    cdef readonly size_t size
    IF UNAME_SYSNAME != 'Windows':
        cdef int o1
    ELSE:
        cdef Py_ssize_t o2
    cdef void * o3
    cdef dict o4

    cdef void * o5(self) noexcept
    cdef bytes o6(self, size_t input, size_t length)

cdef class array2d:
    cdef void * a1
    cdef bint a2
    cdef size_t a3
    cdef size_t a4
    cdef size_t a5
    cdef Py_ssize_t a6[2]
    cdef Py_ssize_t a7[2]
