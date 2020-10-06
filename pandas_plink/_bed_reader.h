int read_bed_chunk(char *filepath, uint64_t nrows, uint64_t ncols,
                   uint64_t row_start, uint64_t col_start,
                   uint64_t row_end, uint64_t col_end,
                   uint8_t *out, uint64_t *strides);
