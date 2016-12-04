from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef("void read_bed(char*, uint64_t, uint64_t, uint64_t*);")

ffibuilder.set_source("_bed_reader", r"""
    #include <stdio.h>
    #include <math.h>

    static void read_bed(char *filepath, uint64_t nrows, uint64_t ncols, uint64_t *out)
    {
        FILE* f = fopen(filepath, "rb");
        fseek(f, 3, SEEK_SET);
        uint64_t e, i, j;

        uint64_t linesize = (uint64_t) ceil(ncols / 4.0);
        char* buff = malloc(linesize);

        char b, b0, b1, p0, p1;

        for (i = 0; i < nrows; ++i)
        {
            e = fread(buff, linesize, 1, f);
            for (j = 0; j < ncols; ++j)
            {
                b = (buff[j/4] >> (2*(j%4))) & 3;

                b0 = b & 1;
                b1 = b >> 1;

                p0 = b0 ^ b1;
                p1 = (b0 | b1) & b0;

                out[i * ncols + j] = (p1 << 1) | p0;
            }
        }

        free(buff);
        fclose(f);
    }
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
