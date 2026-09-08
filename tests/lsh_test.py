import pytest

from tests import shingler_test, minhash_test
from src.lsh import LSHConfiguration, LocalitySensitiveHasher
from src.utils.hash import get_prime_above_bucket_size_in_bytes

def test_lsh():
    shingles_bucket_size_in_byte=4
    shingle_hasher = shingler_test.DynamicShingleHasher(n_bytes=shingles_bucket_size_in_byte)

    config = shingler_test.ShinglerConfiguration(
        type='word', 
        k=3, 
        hasher=shingle_hasher
    )
    _, hashed_shingles, _ = shingler_test.base_test(config)

    n_hashes = 10
    mod_factor = get_prime_above_bucket_size_in_bytes(shingles_bucket_size_in_byte)
    permutator = minhash_test.HashPermutator(
        config=minhash_test.HashPermutatorConfiguration(
            n=n_hashes,
            mod_factor=mod_factor
        )
    )

    assert len(permutator.hash_functions) == n_hashes   

    sig = minhash_test.MinhashGenerator.get_signature(permutator, hashed_shingles)
    assert isinstance(sig, list)
    assert len(sig) == n_hashes
    assert all(isinstance(val, int) for val in sig)

    B=2
    R=5
    lsh = LocalitySensitiveHasher(
        config=LSHConfiguration(
            signature_size=n_hashes,
            b=B,
            r=R,
            signature_item_size_in_bytes=shingles_bucket_size_in_byte,
            lsh_band_bucket_size_in_bytes=4
        )
    )

    hashes = lsh.hashed_bands(sig)
    assert len(hashes) == B
    assert all(isinstance(band_id, int) for band_id, _ in hashes)
    assert all(isinstance(bucket, int) for _, bucket in hashes)
    assert [band_id for band_id, _ in hashes] == list(range(B))

def test_lsh_estimated_threshold():
    config = LSHConfiguration(
        signature_size=100,
        b=20,
        r=5,
        signature_item_size_in_bytes=4,
    )
    lsh = LocalitySensitiveHasher(config)
    assert pytest.approx(lsh.get_estimated_threshold(), 0.0001) == (
        1 / 20
    ) ** (1 / 5)