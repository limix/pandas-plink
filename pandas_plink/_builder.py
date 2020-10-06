from os.path import dirname, join, realpath

from cffi import FFI

ffibuilder = FFI()
ffibuilder.set_unicode(False)

ffibuilder.cdef(
    r"""
    int read_bed_chunk(char*, uint64_t, uint64_t,
                       uint64_t, uint64_t,
                       uint64_t, uint64_t,
                       uint64_t*, uint64_t*);
"""
)

dirname(realpath(__file__))
ffibuilder.set_source(
    "pandas_plink.bed_reader",
    r"""
int read_bed_chunk(char*, uint64_t, uint64_t,
                       uint64_t, uint64_t,
                       uint64_t, uint64_t,
                       uint64_t*, uint64_t*);
""",
    sources=[join("pandas_plink", "_bed_reader.c")],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
