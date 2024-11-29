def quickHash(value: str) -> str:
    # FNV-1a 32-bit hash - simple and reproducible across languages
    fnv_prime = 16777619
    offset_basis = 2166136261
    hash_val = offset_basis
    for byte in value.encode():
        hash_val = hash_val ^ byte
        hash_val = (hash_val * fnv_prime) & 0xFFFFFFFF
    return format(hash_val, "08x")  # 8 hex chars


# rust
#
# fn quickHash(value: &str) -> String {
#   FNV-1a 32-bit hash - simple and reproducible across languages
#   let mut hash: u32 = 2166136261;
#   for byte in value.as_bytes() {
#       hash ^= *byte as u32;
#       hash = hash.wrapping_mul(16777619);
#   }
#   format!("{:08x}", hash)
# }
