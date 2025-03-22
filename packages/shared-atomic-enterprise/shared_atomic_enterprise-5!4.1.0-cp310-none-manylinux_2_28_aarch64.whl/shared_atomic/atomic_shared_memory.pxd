from shared_atomic.atomic_object_backend cimport atomic_object
from libc.limits cimport ULLONG_MAX

cpdef int atomic_shared_memory_remove(str shared_memory_path) except -1
cpdef bytes shared_memory_offset_get(atomic_shared_memory memory, size_t offset = *, char length = *)
cpdef bytes shared_memory_offset_get_and_set(atomic_shared_memory memory, bytes value, size_t offset  = *)
cpdef void shared_memory_offset_store(atomic_shared_memory memory, atomic_shared_memory shared_memory2, size_t offset=*, size_t offset2=*, char length=*) except *
cpdef void shared_memory_offset_store_from_other_types(atomic_shared_memory memory, atomic_object object2, size_t offset=*) except *
cpdef bint shared_memory_offset_compare_and_set(atomic_shared_memory memory, atomic_shared_memory shared_memory2, bytes value, size_t offset=*, size_t offset2=*) except *
cpdef bint shared_memory_offset_compare_with_other_type_and_set(atomic_shared_memory memory, atomic_object object2, bytes value, size_t offset=*) except *
cpdef bytes shared_memory_offset_compare_and_set_value(atomic_shared_memory memory, bytes i, bytes n, size_t offset=*)
cpdef bytes  shared_memory_offset_add_and_fetch(atomic_shared_memory memory, bytes value, size_t offset  = *)
cpdef bytes  shared_memory_offset_sub_and_fetch(atomic_shared_memory memory, bytes value, size_t offset  = *)
cpdef bytes shared_memory_offset_and_and_fetch(atomic_shared_memory memory, bytes value, size_t offset=*)
cpdef bytes shared_memory_offset_or_and_fetch(atomic_shared_memory memory, bytes value, size_t offset=*)
cpdef bytes shared_memory_offset_xor_and_fetch(atomic_shared_memory memory, bytes value, size_t offset=*)
cpdef bytes shared_memory_offset_nand_and_fetch(atomic_shared_memory memory, bytes value, size_t offset=*)
cpdef bytes shared_memory_offset_fetch_and_add(atomic_shared_memory memory, bytes value, size_t offset=*)
cpdef bytes shared_memory_offset_fetch_and_sub(atomic_shared_memory memory, bytes value, size_t offset=*)
cpdef bytes shared_memory_offset_fetch_and_and(atomic_shared_memory memory, bytes value, size_t offset=*)
cpdef bytes shared_memory_offset_fetch_and_or(atomic_shared_memory memory, bytes value, size_t offset=*)
cpdef bytes shared_memory_offset_fetch_and_xor(atomic_shared_memory memory, bytes value, size_t offset=*)
cpdef bytes shared_memory_offset_fetch_and_nand(atomic_shared_memory memory, bytes value, size_t offset=*)

cdef class atomic_shared_memory(atomic_object):
    cdef public bint s1
    cdef str s2
    cdef Py_ssize_t s3[1]
    cdef Py_ssize_t s4[1]
    cdef size_t s5
    cdef readonly int s6



    cpdef int file_sync(self, bint async=*, size_t start=*, size_t length=*) except -1

    cpdef bytes offset_get(self, size_t offset  = *, char length = *)
    cpdef bytes offset_get_and_set(self, bytes value, size_t offset  = *)
    cpdef void offset_store(self, atomic_shared_memory shared_memory2,size_t offset=*, size_t offset2=*, char length=*) except *
    cpdef void offset_store_from_other_types(self, atomic_object object2, size_t offset=*) except *
    cpdef bint offset_compare_and_set(self, atomic_shared_memory shared_memory2, bytes value,size_t offset=*, size_t offset2=*) except *
    cpdef bytes offset_compare_and_set_value(self, bytes i, bytes n, size_t offset  = *)
    cpdef bint offset_compare_with_other_type_and_set(self, atomic_object object2, bytes value, size_t offset=*) except *

    cpdef bytes offset_add_and_fetch(self, bytes value, size_t offset  = *)
    cpdef bytes  offset_sub_and_fetch(self, bytes value, size_t offset  = *)
    cpdef bytes offset_and_and_fetch(self, bytes value, size_t offset=*)
    cpdef bytes offset_or_and_fetch(self, bytes value, size_t offset=*)
    cpdef bytes offset_xor_and_fetch(self, bytes value, size_t offset=*)
    cpdef bytes offset_nand_and_fetch(self, bytes value, size_t offset=*)
    cpdef bytes offset_fetch_and_add(self, bytes value, size_t offset=*)
    cpdef bytes offset_fetch_and_sub(self, bytes value, size_t offset=*)
    cpdef bytes offset_fetch_and_and(self, bytes value, size_t offset=*)
    cpdef bytes offset_fetch_and_or(self, bytes value, size_t offset=*)
    cpdef bytes offset_fetch_and_xor(self, bytes value, size_t offset=*)
    cpdef bytes offset_fetch_and_nand(self, bytes value, size_t offset=*)

    cpdef char [: , ::1] offset_gets(self, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_get_and_sets(self, const char[:,:]  values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef void offset_stores(self,  list other_memories,  size_t[:] offsets, const size_t[:]  offsets2, const char[:] lengths, size_t parallelism=*) except *
    cpdef void offset_stores_from_other_types(self, list other_objects, const size_t[:] offsets, size_t parallelism=*) except *
    cpdef list offset_compare_and_sets(self, list other_memories, const char[:,:] values,  const size_t[:] offsets, const size_t[:]  offsets2, const char[:] lengths, size_t parallelism=*)
    cpdef char [: , ::1] offset_compare_and_set_values(self, const char[:,:] ies, const char[:,:] ns, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *

    cpdef char [: , ::1] offset_add_and_fetches(self, const char[:,:] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_sub_and_fetches(self, const char[:, :] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_and_and_fetches(self, const char[:, :] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_or_and_fetches(self, const char[:, :] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_xor_and_fetches(self, const char[:, :] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_nand_and_fetches(self, const char[:, :] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_fetch_and_adds(self, const char[:, :] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_fetch_and_subs(self, const char[:, :] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_fetch_and_ands(self, const char[:, :] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_fetch_and_ors(self, const char[:, :] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_fetch_and_xors(self, const char[:, :] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *
    cpdef char [: , ::1] offset_fetch_and_nands(self, const char[:, :] values, const size_t[:] offsets, const char[:] lengths, size_t parallelism=*) except *

    cdef void s6(self,  unsigned char[:] mv, unsigned char * reference, size_t length) except *
    cdef void s7(self,  const unsigned char[:] mv, unsigned char * reference, size_t length) except *
    cpdef void offset_memmove(self, mv: object, size_t offset = *, str io_flags =*) except *
    cpdef size_t memdump(self, str file_path, size_t start=*, size_t length=*) except ?ULLONG_MAX
    cdef tuple s8(self, size_t start, size_t length)








