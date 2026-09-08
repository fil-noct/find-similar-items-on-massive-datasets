import pytest
import random
from src.shingler import ShinglerConfiguration, Shingler
from src.utils.hash import DynamicShingleHasher
from src.utils.text import keep_letters_lowercase

def base_test(config: ShinglerConfiguration, custom_input: str = None):
    text = custom_input if custom_input is not None else (
        "While many campuses are struggling with major outbreaks, "
        "some schools have successfully contained the virus."
    )
    s = Shingler(config)
    return s.get_shingles(text), s.get_hashed_shingles(text) if config.hasher else [], text

def test_char_shingler_sliding_window():
    config = ShinglerConfiguration(type='char', k=3)
    shingles, _, text = base_test(config)
    assert len(shingles) == len(text) - 3 + 1
    assert shingles[0] == "Whi"
    assert shingles[1] == "hil"

def test_word_shingler_sliding_window():
    config = ShinglerConfiguration(type='word', k=3)
    shingles, _, _ = base_test(config)
    assert len(shingles) == 15 - 3 + 1
    assert shingles[0] == "While many campuses"
    assert shingles[1] == "many campuses are"

def test_char_shingler_sanitized_length():
    text = "Hello, World!"
    config = ShinglerConfiguration(type='char', k=2, sanitizer=keep_letters_lowercase)
    shingles, _, _ = base_test(config, custom_input=text)
    assert len(shingles) == 12 - 2
    assert shingles[0] == "he"

def test_hashed_shingles_output_structure():
    shingle_hasher = DynamicShingleHasher(n_bytes=4)
    config = ShinglerConfiguration(
        type='word', 
        k=2, 
        hasher=shingle_hasher
    )
    shingles, hashed_shingles, text = base_test(config)
    
    assert len(hashed_shingles) == len(shingles)
    assert all(isinstance(h, int) for h in hashed_shingles)

def test_hashed_shingles_determinism():
    shingle_hasher = DynamicShingleHasher(n_bytes=4)

    config = ShinglerConfiguration(
        type='char', 
        k=3, 
        hasher=shingle_hasher
    )
    s = Shingler(config)
    text = "testing deterministic hash"
    
    hashes_1 = s.get_hashed_shingles(text)
    hashes_2 = s.get_hashed_shingles(text)
    assert hashes_1 == hashes_2

def test_hashed_shingles_missing_hasher_raises_error():
    config = ShinglerConfiguration(type='char', k=2)
    s = Shingler(config)
    with pytest.raises(TypeError, match="hasher"):
        s.get_hashed_shingles("some text")

def test_shingler_k_larger_than_input():
    config = ShinglerConfiguration(type='word', k=10)
    shingles, _, _ = base_test(config, custom_input="short text")
    assert shingles == []

def test_shingler_empty_input():
    config = ShinglerConfiguration(type='char', k=2)
    shingles, _, _ = base_test(config, custom_input="")
    assert shingles == []

@pytest.mark.parametrize("k", [random.randint(1, 10) for _ in range(5)])
def test_random_k_char_shingler(k):
    text = "A randomized test string for char shingling"
    config = ShinglerConfiguration(type='char', k=k)
    s = Shingler(config)
    result = s.get_shingles(text)
    
    expected_len = max(0, len(text) - k + 1)
    assert len(result) == expected_len

@pytest.mark.parametrize("k", [random.randint(1, 5) for _ in range(5)])
def test_random_k_word_shingler(k):
    text = "A randomized test string for word shingling"
    words_count = len(text.split())
    config = ShinglerConfiguration(type='word', k=k)
    s = Shingler(config)
    result = s.get_shingles(text)
    
    expected_len = max(0, words_count - k + 1)
    assert len(result) == expected_len