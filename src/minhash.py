from dataclasses import dataclass
import random

@dataclass(frozen=True)
class PolynomialCoeff:
    """
    Class that represents the linear coefficients (a, b) for a polynomial hash function

    Attributes:
        a (int): multiplicative coefficient.
        b (int): additive coefficient.
    """
    a: int
    b: int

class PolynomialHashFunction:
    """
    Callable polynomial hash function class defined as `h(x) = (a * x + b) % mod`.

    Attributes:
        coeffs (PolynomialCoeff): polynomial coefficients that contains `a` and `b`
        mod (int): modulo value defining the bucket size for the function.
    """
    def __init__(self, coeffs: PolynomialCoeff, mod: int):
        self.coeffs = coeffs
        self.mod = mod

    def __call__(self, x: int) -> int:
        """
        Calculates the hash value for a given integer.

        Args:
            x (int): integer value to hash.

        Returns:
            int: the resulting hash value modulo `mod`.
        """
        return (self.coeffs.a * x + self.coeffs.b) % self.mod

    def __repr__(self) -> str:
        return f"h(x) = ({self.coeffs.a}*x + {self.coeffs.b}) % {self.mod}"

@dataclass
class HashPermutatorConfiguration:
    """
    Configuration class for setting up a `HashPermutator`.

    Attributes:
        n (int): number of unique hash functions (permutations) to generate.
        mod_factor (int): the modulo bound used for the hash functions.

    Raises:
        TypeError: if `n` or `mod_factor` are not positive integers.
        ValueError: if requested `n` exceeds the maximum unique seed combinations possible.
    """
    n: int
    mod_factor: int

    def __post_init__(self):
        if not (isinstance(self.n, int) and self.n > 0):
            raise TypeError("n must be a positive integer")

        if not (isinstance(self.mod_factor, int) and self.mod_factor > 0):
            raise TypeError("mod_factor must be a positive integer")
        
        max_unique_seeds = (self.mod_factor - 1) * self.mod_factor
        if self.n > max_unique_seeds:
            raise ValueError(
                f"n ({self.n}) cannot exceed total available unique seed configurations "
                f"({max_unique_seeds}) for mod_factor={self.mod_factor}."
            )
    
class HashPermutator:
    """
    Class that generates a set of unique pseudo-random hash functions used to simulate permutations.

    Attributes:
        config (HashPermutatorConfiguration): configuration containing permutations count and modulo factor.
        seeds (set[PolynomialCoeff]): set of unique coefficient pairs generated.
        hash_functions (list[PolynomialHashFunction]): list of instantiated unique hash functions.

    Raises:
        RuntimeError: if unique seeds cannot be generated within the maximum attempts limit.
    """
    def __init__(self, config: HashPermutatorConfiguration):
        self.config = config
        self.seeds: set[PolynomialCoeff] = set()
        max_attempts = self.config.n * 1000
        attempts = 0
        while len(self.seeds) < self.config.n:
            if attempts >= max_attempts:
                raise RuntimeError(
                    f"Failed to generate {self.config.n} unique seeds after {attempts} attempts."
                )
            
            coeffs = PolynomialCoeff(
                a=random.randint(1, self.config.mod_factor - 1),
                b=random.randint(0, self.config.mod_factor - 1)
            )
            self.seeds.add(coeffs)

        self.hash_functions = [
            PolynomialHashFunction(polynomial_seed, self.config.mod_factor) 
            for polynomial_seed in self.seeds
        ]

    def hash(self, index: int):
        """
        Applies all permutation hash functions to a single input index.

        Args:
            index (int): the input value to hash.

        Returns:
            list[int]: a list of hash values corresponding to each hash function in the permutator.
        """
        return [h(index) for h in self.hash_functions]

class MinhashGenerator:
    @staticmethod
    def get_signature(permutator: HashPermutator, shingles: list[int]):
        """
        Generates the minhash signature for a list of hashed shingles.

        Args:
            permutator (HashPermutator): the permutator object that simulates permutation using polynomial hash functions.
            shingles (list[int]): list of integer shingle values.

        Returns:
            list[int]: the minhash signature vector containing minimum hash values across all `shingle`.

        Raises:
            ValueError: if the input `shingles` list is empty or `None`.
        """
        if not shingles or len(shingles)==0:
            raise ValueError("invalid shingles param")
        
        all_hashes = [permutator.hash(s) for s in shingles]
        return [min(hashes_per_func) for hashes_per_func in zip(*all_hashes)]