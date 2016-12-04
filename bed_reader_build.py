from cffi import FFI
ffibuilder = FFI()

ffibuilder.cdef("void read_bed(char*, uint64_t, uint64_t, uint64_t*);")

ffibuilder.set_source("_bed_reader",
r"""
    #include <stdio.h>
    #include <math.h>

    static void read_bed(char *filepath, uint64_t nrows, uint64_t ncols, uint64_t *out)
    {
        FILE* f = fopen(filepath, "rb");
        fseek(f, 3, SEEK_SET);
        uint64_t e;

        uint64_t linesize = (uint64_t) ceil(ncols / 4.0);
        char* buff = malloc(linesize);

        for (uint64_t i = 0; i < nrows; ++i)
        {
            e = fread(buff, linesize, 1, f);
            for (uint64_t j = 0; j < ncols; ++j)
            {
                out[i * ncols + j] = 3 & (buff[j/3] >> (2*(j%4)));
            }
        }

        free(buff);
        fclose(f);
    }
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
