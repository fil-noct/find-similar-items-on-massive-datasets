import hashlib
from sympy import nextprime

def hash_to_n_byte_int(data: bytes, n_bytes: int) -> int:
    if n_bytes <= 0 or n_bytes > 64:
        raise ValueError("n_bytes must be a positive integer lower than 64 (0 < n <= 64)")
    
    digest = hashlib.blake2b(data, digest_size=n_bytes).digest()
    return int.from_bytes(digest, byteorder="big")

class DynamicShingleHasher:
    def __init__(self, n_bytes: int):
        self.n_bytes = n_bytes

    def __call__(self, s: str) -> int:
        return hash_to_n_byte_int(data=s.encode("utf-8"), n_bytes=self.n_bytes)

def get_prime_above_bucket_size_in_bytes(n_bytes: int) -> int:
    if not isinstance(n_bytes, int) or n_bytes <= 0 or n_bytes > 64:
        raise ValueError("n_bytes must be an integer between 1 and 64")
    
    bits = 8 * n_bytes
    domain_upper_bound = (2 ** bits) - 1
    return nextprime(domain_upper_bound)

def get_required_bytes_to_store_int(n: int) -> int:
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    if n == 0:
        return 1
    
    return (n.bit_length() + 7) // 8