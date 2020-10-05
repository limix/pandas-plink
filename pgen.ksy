meta:
  id: pgen
  file-extension: bed
  bit-endian: le
  endian: le
seq:
  - id: header
    type: header
enums:
  storage_type:
    0x00: plink1_sample_major
    0x01: plink1_variant_major
    0x02: plink2_simple
    0x03: plink2_fw_unphased
    0x04: plink2_fw_phased
    0x10: plink2_standard
  genotype:
    0x00: homozygote_11
    0x01: missing
    0x02: heterozygote
    0x03: homozygote_22

types:
  header:
    seq:
      - id: magic
        type: u2
      - id: storage_type
        type: u1
        enum: storage_type
      - id: dim
        type:
          switch-on: storage_type
          cases:
              'storage_type::plink2_simple': dim
              'storage_type::plink2_fw_unphased': dim
              'storage_type::plink2_fw_phased': dim
              'storage_type::plink2_standard': dim
      - id: storage
        type:
          switch-on: storage_type
          cases:
              'storage_type::plink1_sample_major': plink1_genotype_data
              'storage_type::plink1_variant_major': plink1_genotype_data
              'storage_type::plink2_simple': dim
              'storage_type::plink2_fw_unphased': dim
              'storage_type::plink2_fw_phased': dim
              'storage_type::plink2_standard': dim
  dim:
    seq:
      - id: nvariants
        type: u4
      - id: nsamples
        type: u4
  plink1_genotype_data:
    seq:
      - id: genotype
        type: b2
        enum: genotype
        repeat: eos
