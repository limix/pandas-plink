int write_bed_header(char *filepath, uint8_t major);
int write_bed_chunk(char *filepath, uint64_t ncols, uint64_t row_chunk, uint8_t *data, uint64_t *strides);
