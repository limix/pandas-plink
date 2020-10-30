#include <math.h>
#include <stdio.h>
#include <stdlib.h>

/*             xy  */
/* 0d = 00b -> 00b */
/* 1d = 01b -> 10b */
/* 2d = 10b -> 11b */
/* 3d = 11b -> 01b */
/* then shift to the left */
static inline uint8_t convert(uint8_t v)
{
        uint8_t x = (v >> 1) & 0x01;
        uint8_t y = (v >> 0) & 0x01;

        uint8_t new_x = (x & ~y) | (~x & y);
        uint8_t new_y = x;

        return ((new_x << 1) | (new_y << 0)) << 6;
}

int write_bed_header(char *filepath, uint8_t major)
{
        FILE *f = fopen(filepath, "wb");
        if (f == NULL)
        {
                fprintf(stderr, "Couldn't open %s to write.\n", filepath);
                return -1;
        }

        uint16_t magic_number = 0x1b6c;
        if (fwrite(&magic_number, sizeof(magic_number), 1, f) != 1)
        {
                fprintf(stderr, "File error: %d.\n", ferror(f));
                fclose(f);
                return -1;
        }

        if (fwrite(&major, sizeof(major), 1, f) != 1)
        {
                fprintf(stderr, "File error: %d.\n", ferror(f));
                fclose(f);
                return -1;
        }

        fclose(f);
        return 0;
}

int write_bed_chunk(char *filepath, uint64_t ncols, uint64_t row_chunk, uint8_t *data, uint64_t *strides)
{
        FILE *f = fopen(filepath, "ab");
        if (f == NULL)
        {
                fprintf(stderr, "Couldn't open %s to append.\n", filepath);
                return -1;
        }

        for (uint64_t r = 0; r < row_chunk; ++r)
        {
                uint64_t c = 0;
                for (; c < ncols - ncols % 4; c += 4)
                {
                        uint8_t byte = convert(data[r * strides[0] + (c + 0) * strides[1]]);
                        byte >>= 2;
                        byte |= convert(data[r * strides[0] + (c + 1) * strides[1]]);
                        byte >>= 2;
                        byte |= convert(data[r * strides[0] + (c + 2) * strides[1]]);
                        byte >>= 2;
                        byte |= convert(data[r * strides[0] + (c + 3) * strides[1]]);
                        if (fwrite(&byte, 1, 1, f) != 1)
                        {
                                fprintf(stderr, "File error: %d.\n", ferror(f));
                                fclose(f);
                                return -1;
                        }
                }
                if (ncols % 4 > 0)
                {
                        uint8_t byte = 0;
                        for (uint64_t i = 0; i < ncols % 4; ++i)
                        {
                                byte >>= 2;
                                byte |= convert(data[r * strides[0] + (c + i) * strides[1]]);
                        }
                        byte >>= 2 * (4 - ncols % 4);
                        if (fwrite(&byte, 1, 1, f) != 1)
                        {
                                fprintf(stderr, "File error: %d.\n", ferror(f));
                                fclose(f);
                                return -1;
                        }
                }
        }

        fclose(f);
        return 0;
}
