#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define MIN(a, b) ((a > b) ? b : a)

void read_bed_chunk(uint8_t *buff, uint64_t nrows, uint64_t ncols,
                    uint64_t row_start, uint64_t col_start, uint64_t row_end,
                    uint64_t col_end, uint8_t *out, uint64_t *strides)
{
    char b, b0, b1, p0, p1;
    uint64_t r;
    uint64_t c, ce;
    uint64_t row_size;

    // in bytes
    row_size = (ncols + 3) / 4;

    r = row_start;
    buff += r * row_size + col_start / 4;

    while (r < row_end)
    {
        for (c = col_start; c < col_end;)
        {
            b = buff[(c - col_start) / 4];

            b0 = b & 0x55;
            b1 = (b & 0xAA) >> 1;

            p0 = b0 ^ b1;
            p1 = (b0 | b1) & b0;
            p1 <<= 1;
            p0 |= p1;
            ce = MIN(c + 4, col_end);
            for (; c < ce; ++c)
            {
                out[(r - row_start) * strides[0] +
                    (c - col_start) * strides[1]] = p0 & 3;
                p0 >>= 2;
            }
        }
        ++r;
        buff += row_size;
    }
}
