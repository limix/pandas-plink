from cffi import FFI
from os.path import dirname, realpath, join

ffibuilder = FFI()

ffibuilder.cdef(r"""
    int read_bed_chunk(char*, uint64_t, uint64_t,
                       uint64_t, uint64_t,
                       uint64_t, uint64_t,
                       uint64_t*);
""")

dirname(realpath(__file__))
ffibuilder.set_source("pandas_plink.bed_reader", "",
                      sources=[join('pandas_plink', '_bed_reader.c')])

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
