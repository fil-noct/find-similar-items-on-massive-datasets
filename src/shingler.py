from dataclasses import dataclass
from typing import Literal, Callable, get_args

ShinglerType = Literal["char", "word"]

@dataclass
class ShinglerConfiguration:
    """
        Shingler configuration class.

        Attributes:
            type (ShinglerType): Choose between 'char' or 'word' based shingling, 
                'word' based shingling uses the space char to split the text in chunks.
            k (int): specify the sliding window size.
            sanitizer (Callable[[str], str] | None): optional function to pre-process the text before shingling.
            hasher (Callable[[str], int] | None): optional function to hash each shingle.

        Raises:
            ValueError: if `type` is not in `['char', 'word']`
            ValueError: if `k` is not a positive integer.
            TypeError: if `sanitizer` or `hasher` are provided but not callable.
    """
    type: ShinglerType 
    k: int
    sanitizer: Callable[[str], str] | None = None
    hasher: Callable[[str], int] | None = None
    
    def __post_init__(self):
        valid_types = get_args(ShinglerType)
        
        if self.type not in valid_types:
            raise ValueError(f"type must be one of {valid_types}, got '{self.type}'")
        
        if not (isinstance(self.k, int) and self.k > 0):
            raise ValueError("k must be a positive integer")

        if self.sanitizer is not None and not callable(self.sanitizer):
            raise TypeError("sanitizer must be callable or None")
            
        if self.hasher is not None and not callable(self.hasher):
            raise TypeError("hasher must be callable or None")

class Shingler:
    """
        Shingler class that allows to calculate and retrieve the shingles of a `text`,
        based on the specified configuration.

        Attributes:
            config (ShinglerConfiguration): The shingler configuration instance.
            k (int): specify the sliding window size.
    """
    def __init__(self, config: ShinglerConfiguration):
        self.config = config

    def _process_char(self, data: str) -> list[str]:
        k = self.config.k
        if len(data) < k:
            return []
        return [data[i:i + k] for i in range(len(data) - k + 1)]

    def _process_word(self, data: str) -> list[str]:
        words = data.split()
        k = self.config.k
        if len(words) < k:
            return []
        return [' '.join(words[i:i + k]) for i in range(len(words) - k + 1)]

    def _processor(self, data: str) -> list[str]:
        if self.config.type == "char":
            return self._process_char(data)
        elif self.config.type == "word":
            return self._process_word(data)
        else:
            raise TypeError("type must be 'char' or 'word'")

    def get_shingles(self, text: str) -> list[str]:
        """
        Calculates the shingles of the specified `text`.

        If the sanitizer param is set in the shingler configuration, 
        it gets executed before processing the `text`.

        Args:
            text (str): The text to shingle.

        Returns:
            list[str]: The calculated shingles as a list of strings,
              please note that if the provided text is too short to produce at least a shingle the list is empty.
        """
        if callable(self.config.sanitizer):
            return self._processor(self.config.sanitizer(text))
        else:
            return self._processor(text)

    def get_hashed_shingles(self, text: str) -> list[int]:
        """
        Calculates the hashed shingles of the specified text.

        If the sanitizer param is set in the shingler configuration, 
        it gets executed before processing the text.
        Once the shingling ended producing the list of string,
        each shingle get hashed using the specified function based on instance configuration.  

        Args:
            text (str): The text to shingle.

        Returns:
            list[int]: The calculated hashed shingles as a `list` of `int`, please note that the bucket size and the hash techniques depends on the configuration of the object and if the provided `text` is too short to produce at least a shingle the list is empty
        Raises:
            TypeError:
                the `hasher` function must be set in the `ShinglerConfiguration`
        """
        if not callable(self.config.hasher):
            raise TypeError("hasher not set in the ShinglerConfiguration")

        return [self.config.hasher(shingle) for shingle in self.get_shingles(text)]