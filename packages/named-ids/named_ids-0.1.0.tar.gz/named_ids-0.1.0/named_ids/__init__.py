"""
named_ids - Human readable unique identifiers

This module provides functionality to generate human-readable IDs using combinations
of words from different parts of speech.
"""

import os
import random
from typing import Literal, Optional, List, Dict, Tuple

SizeType = Literal["tiny", "small", "medium", "large", "huge"]

_current_size: SizeType = "small" # default
_indices: Dict[str, int] = {
    "nouns": 0,
    "adjectives": 0,
    "verbs": 0,
    "adverbs": 0,
    "numbers": 0
}

# Prime steps for each category
_primes: Dict[str, int] = {
    "nouns": 2,
    "adjectives": 3,
    "verbs": 5,
    "adverbs": 7,
    "numbers": 11
}

# Word lists
_words: Dict[str, List[str]] = {
    "nouns": [],
    "adjectives": [],
    "verbs": [],
    "adverbs": []
}

_number_range = list(range(2, 1000))

def _load_words() -> None:
    """Load word lists from asset files."""
    module_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(module_dir)), "assets")
    
    if not os.path.exists(assets_dir):
        assets_dir = os.path.join(module_dir, "assets")
    
    # Load each word list
    for word_type in _words.keys():
        file_path = os.path.join(assets_dir, f"{word_type}.txt")
        try:
            with open(file_path, "r") as file:
                _words[word_type] = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find word list file: {file_path}")

def _ensure_words_loaded() -> None:
    """Ensure word lists are loaded before use."""
    if not any(_words.values()):
        _load_words()

def _validate_prime_steps() -> None:
    """Validate that prime steps are not divisors of their respective array lengths."""
    for word_type, prime in _primes.items():
        if word_type == "numbers":
            array_length = len(_number_range)
        else:
            array_length = len(_words[word_type])
        
        if array_length > 0 and array_length % prime == 0:
            # Find the next prime
            is_odd = prime % 2 != 0
            new_prime = prime + 1 + int(is_odd)
            while array_length % new_prime == 0 or not _is_prime(new_prime):
                new_prime += 1 + int(is_odd)
            _primes[word_type] = new_prime

def _is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    for i in range(5, int(n**0.5) + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True

def _randomize_indices() -> None:
    """Initialize indices with random starting positions and shuffle word lists."""
    # Shuffle all word lists
    for word_type in _words.keys():
        if _words[word_type]:
            random.shuffle(_words[word_type])
    
    # Shuffle number range for "huge" size
    random.shuffle(_number_range)
    
    # Randomize starting indices
    for word_type in _indices.keys():
        if word_type == "numbers":
            array_length = len(_number_range)
        else:
            array_length = len(_words[word_type])
        
        if array_length > 0:
            _indices[word_type] = random.randint(0, array_length - 1)

def _step_index(word_type: str) -> int:
    """Step the index for a word type and return the new index."""
    if word_type == "numbers":
        array_length = len(_number_range)
    else:
        array_length = len(_words[word_type])
    
    if array_length == 0:
        return 0
    
    _indices[word_type] = (_indices[word_type] + _primes[word_type]) % array_length
    return _indices[word_type]

def _get_word_at_index(word_type: str, index: Optional[int] = None) -> str:
    """Get a word from a specific word type at the given index or current index."""
    if index is None:
        index = _indices[word_type]
    
    if word_type == "numbers":
        return str(_number_range[index % len(_number_range)])
    else:
        return _words[word_type][index % len(_words[word_type])]

def set(size: SizeType = "small") -> None:
    """
    Set the size of the generated IDs and recalculate prime steps and random indices.
    
    Args:
        size: The size of IDs to generate.
              - "tiny": nouns only
              - "small": adjectives + nouns
              - "medium": adjectives + nouns + verbs
              - "large": adverbs + adjectives + nouns + verbs
              - "huge": number + adverbs + adjectives + nouns + verbs
    """
    if size not in ["tiny", "small", "medium", "large", "huge"]:
        raise ValueError(f"Invalid size: {size}")
    global _current_size
    _ensure_words_loaded()
    _validate_prime_steps()
    _randomize_indices()
    _current_size = size

def next() -> str:
    """
    Generate the next ID in the sequence based on the current size setting.
    
    Returns:
        A human-readable ID string.
    """
    _ensure_words_loaded()
    
    components = []
    
    if _current_size == "huge":
        components.append(_get_word_at_index("numbers", _step_index("numbers")))
    
    if _current_size in ["large", "huge"]:
        components.append(_get_word_at_index("adverbs", _step_index("adverbs")))
    
    if _current_size in ["small", "medium", "large", "huge"]:
        components.append(_get_word_at_index("adjectives", _step_index("adjectives")))
    
    # All sizes include nouns
    components.append(_get_word_at_index("nouns", _step_index("nouns")))
    
    if _current_size in ["medium", "large", "huge"]:
        components.append(_get_word_at_index("verbs", _step_index("verbs")))
    
    return "_".join(components)

def sample(size: Optional[SizeType] = None) -> str:
    """
    Generate a random ID without stepping the sequence.
    
    Args:
        size: The size of ID to generate. If None, uses the current size setting.
        
    Returns:
        A randomly generated human-readable ID string.
    """
    _ensure_words_loaded()
    
    if size is None:
        size = _current_size
    elif size not in ["tiny", "small", "medium", "large", "huge"]:
        raise ValueError(f"Invalid size: {size}")
    
    components = []
    
    if size == "huge":
        components.append(str(random.choice(_number_range)))
    
    if size in ["large", "huge"]:
        components.append(random.choice(_words["adverbs"]))
    
    if size in ["small", "medium", "large", "huge"]:
        components.append(random.choice(_words["adjectives"]))
    
    # All sizes include nouns
    components.append(random.choice(_words["nouns"]))
    
    if size in ["medium", "large", "huge"]:
        components.append(random.choice(_words["verbs"]))
    
    return "_".join(components)

# Initialize the module
_ensure_words_loaded()
_validate_prime_steps()
_randomize_indices()  # Initialize with random starting positions
