import pytest
from src.minhash import HashPermutatorConfiguration, HashPermutator, MinhashGenerator
import tests.shingler_test as shingler_test
from src.utils.hash import get_prime_above_bucket_size_in_bytes

def test_minhash_simple():
    doc_shingle = {
        "d1": [0, 2],
        "d2": [1, 2],
        "d3": [0, 1, 3]
    }
    n_hashes = 2
    mod_factor = 5
    permutator = HashPermutator(
        config=HashPermutatorConfiguration(
            n=n_hashes,
            mod_factor=mod_factor
        )
    )
    assert len(permutator.hash_functions) == n_hashes    
    signatures = {}
    for doc, shingles in doc_shingle.items():
        sig = MinhashGenerator.get_signature(permutator, shingles)
        signatures[doc] = sig

        assert isinstance(sig, list)
        assert len(sig) == n_hashes
        assert all(isinstance(val, int) for val in sig)
        assert all(0 <= val < mod_factor for val in sig)

def test_minhash_with_shingling():
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
    permutator = HashPermutator(
        config=HashPermutatorConfiguration(
            n=n_hashes,
            mod_factor=mod_factor
        )
    )

    assert len(permutator.hash_functions) == n_hashes   

    sig = MinhashGenerator.get_signature(permutator, hashed_shingles)
    assert isinstance(sig, list)
    assert len(sig) == n_hashes
    assert all(isinstance(val, int) for val in sig)
    assert all(0 <= val < mod_factor for val in sig)

def test_minhash_safe_exit():
    with pytest.raises(ValueError):
        HashPermutatorConfiguration(n=100, mod_factor=3)

    with pytest.raises(TypeError):
        HashPermutatorConfiguration(n=-1, mod_factor=5)

    with pytest.raises(TypeError):
        HashPermutatorConfiguration(n=2, mod_factor=0)
