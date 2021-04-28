
from libc.math cimport sqrt


def cyintegrate(float a, float b, int N):
    cdef:
        int i
        float dx, s = 0.0
        float *p_dx = &dx

    p_dx[0] = (b - a) / N
    for i in range(N):
        s += sqrt(a + i * dx)
    return s * p_dx[0]

def py_fact(n):
    if n <= 1:
        return 1
    return n * py_fact(n - 1)

## This does not improve performance over py_fact because the typed_fact() returns a python object
## this does not allow cython to improve the performace
def typed_fact(long n):
    if n <= 1:
        return 1
    return n * typed_fact(n - 1)

cdef long c_fact(long n):
    if n <= 1:
        return 1
    return n * c_fact(n - 1)

def wrap_c_fact(n):
    return c_fact(n)


### Cython struct and Union
cdef struct mycpx:
    float real
    float imag

cdef union uu:
    int a
    short b, c

def print_cpx(float r, float i):
    cdef mycpx a = mycpx(r, i)
    print(a)

# ENUMs are not available to outside code
cdef enum PRIMARIES:
    RED = 1
    YELLOW = 3
    BLUE = 5

cdef enum SECONDARIES:
    ORANGE, GREEN, PURPLE

