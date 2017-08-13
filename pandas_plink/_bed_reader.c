#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define MIN(a, b) ((a > b) ? b : a)

#ifdef _MSC_VER
 #if (_MSC_VER <= 1500)
  typedef unsigned __int64     uint64_t;
 #else
 # include <stdint.h>
 #endif
#else
# include <stdint.h>
#endif

int read_bed_chunk(char *filepath, uint64_t nrows, uint64_t ncols,
                          uint64_t row_start, uint64_t col_start,
                          uint64_t row_end, uint64_t col_end,
                          uint64_t *out, uint64_t *strides)
{
        char b, b0, b1, p0, p1;
        uint64_t r;
        uint64_t c, ce;
        uint64_t row_chunk;
        uint64_t row_size;
        FILE* f;
        char* buff;

        assert(sizeof(uint64_t) == 4);
        assert(sizeof(char) == 1);
        assert(col_start % 4 == 0);

        // in bytes
        row_chunk = (col_end - col_start + 3) / 4;
        // in bytes
        row_size = (ncols + 3) / 4;

        f = fopen(filepath, "rb");
        if (f == NULL)
        {
                fprintf(stderr, "Couldn't open %s.\n", filepath);
                return -1;
        }

        buff = malloc(row_chunk * sizeof(char));
        if (buff == NULL)
        {
                fprintf(stderr, "Not enough memory.\n");
                fclose(f);
                return -1;
        }

        r = row_start;

        while (r < row_end)
        {
                fseek(f, 3 + r * row_size + col_start / 4, SEEK_SET);

                if (fread(buff, row_chunk, 1, f) != 1)
                {
                        if (feof(f))
                        {
                                fprintf(stderr, "Error reading %s: unexpected end of file.\n", filepath);
                                free(buff);
                                fclose(f);
                                return -1;
                        }
                        if (ferror(f))
                        {
                                fprintf(stderr, "File error: %d.\n", ferror(f));
                                free(buff);
                                fclose(f);
                                return -1;
                        }
                }


                for (c = col_start; c < col_end; )
                {
                        b = buff[(c - col_start)/4];

                        b0 = b & 0x55;
                        b1 = (b & 0xAA) >> 1;

                        p0 = b0 ^ b1;
                        p1 = (b0 | b1) & b0;
                        p1 <<= 1;
                        p0 |= p1;
                        ce = MIN(c + 4, col_end);
                        for (; c < ce; ++c)
                        {
                                out[(r - row_start) * strides[0] + (c - col_start) * strides[1]] = p0 & 3;
                                p0 >>= 2;
                        }
                }
                ++r;
        }

        free(buff);
        fclose(f);
        return 0;
}
