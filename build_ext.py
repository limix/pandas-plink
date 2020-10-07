import os
from os.path import join

from cffi import FFI

ffibuilder = FFI()
ffibuilder.set_unicode(False)

folder = os.path.dirname(os.path.abspath(__file__))

with open(join(folder, "pandas_plink", "_bed_reader.h"), "r") as f:
    ffibuilder.cdef(f.read())

with open(join(folder, "pandas_plink", "_bed_reader.c"), "r") as f:
    reader_file = f.read()

with open(join(folder, "pandas_plink", "_bed_writer.h"), "r") as f:
    ffibuilder.cdef(f.read())

with open(join(folder, "pandas_plink", "_bed_writer.c"), "r") as f:
    writer_file = f.read()

c_content = f"{reader_file}\n{writer_file}"
ffibuilder.set_source("pandas_plink.bed_reader", c_content, language="c")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
