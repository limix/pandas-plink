from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef(r"""
    int read_bed(char*, uint64_t, uint64_t, uint64_t*, uint64_t,
                  void (*cb_iter)(void*),
                  void*);
    extern "Python" void cb_iter(void*);
""")

ffibuilder.set_source("_bed_reader", r"""
    #include <stdio.h>
    #include <math.h>
    #include <assert.h>

    #define MIN( a, b ) ( ( a > b) ? b : a )

    static int read_bed(char *filepath, uint64_t nrows, uint64_t ncols,
                         uint64_t *out, uint64_t nint,
                         void (*cb_iter)(void*),
                         void *pb)
    {
            assert(sizeof(uint64_t) == 4);
            assert(sizeof(char) == 1);

            FILE* f = fopen(filepath, "rb");
            fseek(f, 3, SEEK_SET);
            uint64_t i, j, jj_s, jj_e;
            size_t e;

            uint64_t ls = (uint64_t) ceil(ncols / 4.0);

            nint = MIN(nint, nrows);

            uint64_t row_chunk = ceil(nrows / ((double) nint));
            char* buff = malloc(ls * row_chunk * sizeof(char));

            char b, b0, b1, p0, p1;
            size_t row_start = 0, row_end;

            while (row_start < nrows)
            {
                row_end = MIN(row_start + row_chunk, nrows);
                e = fread(buff, ls, row_end - row_start, f);
                if (e < row_end - row_start)
                {
                    e = ferror(f);
                    if (e)
                    {
                        fprintf(stderr, "File error: %zu.\n", e);
                        return e;
                    }
                }

                for (i = row_start; i < row_end; ++i)
                {
                    for (j = 0; j < ncols; j+=4)
                    {
                        b = buff[(i - row_start) * ls + j/4];

                        b0 = b & 0x55;
                        b1 = (b & 0xAA) >> 1;

                        p0 = b0 ^ b1;
                        p1 = (b0 | b1) & b0;
                        p1 <<= 1;
                        p0 |= p1;
                        jj_s = i * ncols + j;
                        jj_e = MIN(jj_s + 4, (i+1) * ncols);
                        for (; jj_s < jj_e; ++jj_s)
                        {
                            out[jj_s] = p0 & 3;
                            p0 >>= 2;
                        }
                    }
                }
                row_start = row_end;
                cb_iter(pb);
            }

            free(buff);
            fclose(f);
            return 0;
    }
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
