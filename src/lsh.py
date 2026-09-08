from dataclasses import dataclass
from src.utils.hash import hash_to_n_byte_int

@dataclass(frozen=True)
class LSHConfiguration:
    """
    Configuration class for setting up a `LocalitySensitiveHasher`.

    Attributes:
        signature_size (int): total length of the minhash signature.
        signature_item_size_in_bytes (int): bucket size in bytes of the minhash signature single element.
        b (int): number of bands to divide the signature into.
        r (int): number of rows per band.
        lsh_band_bucket_size_in_bytes (int): bucket size in bytes of the bands.

    Raises:
        TypeError: if `b` or `r` are not positive integers.
        ValueError: if the condition `signature_size = b * r` gets violated.
        TypeError: if `signature_item_size_in_bytes` or `lsh_band_bucket_size_in_bytes` are not positive integers.

    """
    signature_size: int
    b: int
    r: int
    signature_item_size_in_bytes: int
    lsh_band_bucket_size_in_bytes:int = 4

    def __post_init__(self):
        if not (isinstance(self.b, int) and self.b > 0):
            raise TypeError("b must be a positive integer")
        
        if not (isinstance(self.r, int) and self.r > 0):
            raise TypeError("r must be a positive integer")
        
        if not (self.signature_size == (self.b * self.r)):
            raise ValueError(f"violation of condition signature_size ({self.signature_size}) = b ({self.b}) * r ({self.r})")
        
        if not (isinstance(self.signature_item_size_in_bytes, int) and self.signature_item_size_in_bytes > 0):
            raise TypeError("signature_item_size_in_bytes must be a positive integer")
        
        if not (isinstance(self.lsh_band_bucket_size_in_bytes, int) and self.lsh_band_bucket_size_in_bytes > 0):
            raise TypeError("lsh_band_bucket_size_in_bytes must be a positive integer")

class LocalitySensitiveHasher:
    """
    Class that implements Locality Sensitive Hashing (LSH) for minhash signatures
    to identify candidate duplicate items.

    Attributes:
        config (LSHConfiguration): configuration containing `signature size`, `bands`, and `rows`.
    """
    def __init__(self, config: LSHConfiguration):
        self.config = config

    def get_estimated_threshold(self)->float:
        """
        Calculates the estimated Jaccard similarity threshold based on the instance configuration.
        Returns:
            float: the estimated Jaccard similarity calculated as (1/b)^(1/r).
        """
        return (1/self.config.b)**(1/self.config.r)

    def hashed_bands(self, signature: list[int])->list[tuple[int, int]]:
        """
        Splits a minhash signature into `b` bands of `r` rows and hashes each band to a bucket integer.

        Args:
            signature (list[int]): minhash signature vector to be split into bands and hashed.

        Returns:
            list[tuple[int, int]]: list of tuples where each element contains `(band_index, bucket_hash)`.

        Raises:
            ValueError: if the size of the provided `signature` length does not match the configured `signature_size = b * r`.
        """
        if not len(signature)==self.config.signature_size:
            raise ValueError("the provided signature length does not match the configured `signature_size = b * r`")   
          
        bands = [signature[i:i+self.config.r] for i in range(0, len(signature), self.config.r)]      
        hashed_bands = []
        for i, band in enumerate(bands):
            try:
                band_bytes = b"".join(
                    val.to_bytes(self.config.signature_item_size_in_bytes, byteorder="big")
                    for val in band
                )
            except OverflowError as e:
                raise ValueError(
                    f"signature value exceeded the capacity of {self.config.signature_item_size_in_bytes} bytes."
                ) from e
            
            bucket_hash = hash_to_n_byte_int(band_bytes, n_bytes=self.config.lsh_band_bucket_size_in_bytes)
            hashed_bands.append((i, bucket_hash))
            
        return hashed_bands