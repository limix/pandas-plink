from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef(r"""
    void read_bed(char*, uint64_t, uint64_t, uint64_t*, uint64_t,
                  void (*cb_iter)());
    extern "Python" void cb_iter();
""")

ffibuilder.set_source("_bed_reader", r"""
    #include <stdio.h>
    #include <math.h>

    #define MIN( a, b ) ( ( a > b) ? b : a )

    static void read_bed(char *filepath, uint64_t nrows, uint64_t ncols,
                         uint64_t *out, uint64_t nint, void (*cb_iter)())
    {
            FILE* f = fopen(filepath, "rb");
            fseek(f, 3, SEEK_SET);
            uint64_t e, i, j;

            uint64_t linesize = (uint64_t) ceil(ncols / 4.0);

            uint64_t row_chunk = ceil(nrows / ((double) nint));
            char* buff = malloc(linesize * row_chunk);

            char b, b0, b1, p0, p1;
            uint64_t row_start = 0, row_end;

            while (row_start < nrows)
            {
                row_end = MIN(row_start + row_chunk, nrows);
                e = fread(buff, linesize, row_end - row_start, f);

                for (i = row_start; i < row_end; ++i)
                {
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
                row_start = row_end;
            }

            free(buff);
            fclose(f);
    }
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
