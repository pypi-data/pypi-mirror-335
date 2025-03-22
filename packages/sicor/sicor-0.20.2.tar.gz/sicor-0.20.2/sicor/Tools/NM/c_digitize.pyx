cimport numpy as np
import numpy as np


DTYPE = int
ctypedef np.int_t DTYPE_t

#@cython.boundscheck(False) # turn of bounds-checking for entire function
def c_digitize(np.ndarray[np.float64_t, ndim=1] data,
               np.ndarray[np.float64_t, ndim=1] bins):
    """Cython replacement of np.digitize."""
    cdef Py_ssize_t ii
    cdef float bin_l,bin_d,bin_dn,dd
    cdef int bin_nn
    cdef int bin_map[2000]
    cdef int bi,bf
    cdef np.ndarray[DTYPE_t, ndim=1] ret = np.zeros(data.shape[0], dtype=DTYPE)


    bin_nn = len(bin_map)
    bin_l = bins[0]
    bin_d = bins[-1]-bins[0]
    bin_dn = bin_d/bin_nn


    bi=0
    for ii in range(bin_nn):
        if bin_l+ii*bin_dn>bins[bi]:
            bi+=1
        bin_map[ii] = bi

    for ii in range(data.shape[0]):
        bf = int((data[ii]-bin_l)/bin_dn)
        if bf<1:
            bf = 1
        if bf>1999:
            bf=1999

        bi = bin_map[bf]

        if data[ii]>bins[bi]:
            bi+=1
        ret[ii] = bi

    return ret
