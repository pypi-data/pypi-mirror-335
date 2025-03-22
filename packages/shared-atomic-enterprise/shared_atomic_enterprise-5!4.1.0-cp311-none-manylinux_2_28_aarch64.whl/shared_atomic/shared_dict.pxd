# distutils: language = c++

cdef cppclass ConcurrentHashMap:
    size_t * size
    size_t * matrix_length

cdef class shared_dict:
    cdef ConcurrentHashMap * s1
    cdef readonly bytes file_name
    cdef size_t * s2
    cdef dict     s3
    cpdef int insert(self,object input_key, object input_value) except -1
    cpdef list get(self,object input_key)
    cpdef int remove(self,object input_key) except -1
    cpdef int expansion(self, size_t parallelism=*) except -1

cpdef int dict_insert(shared_dict target,object input_key, object input_value) except -1
cpdef list dict_get(shared_dict target ,object input_key)
cpdef int dict_remove(shared_dict target,object input_key) except -1