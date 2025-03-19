# Named IDs

A Python module for generating human-readable unique identifiers.

## Installation

```bash
pip install named_ids
```

## Usage

The default size is "small" (adjective + noun). Here's how to use the module:

```python
import named_ids

# Optional. Set a seed for reproducible results
random.seed(42)

# Optional. Only needed if you want to use a different size than the default (small)
named_ids.set("large")

# Generate ID
print(named_ids.next())

# Or just sample 
print(named_ids.sample()) # defaults to the one set
print(named_ids.sample("huge")) # can also set the size
```

`next()` ensures unique IDs by stepping through combinations sequentially. `sample()` provides random IDs without maintaining sequence.

## Size Options

| Name   | Pool Size           | Components               | Example             |
|--------|---------------------|--------------------------|---------------------|
| tiny   | 1,5 thousand               | noun                     | `queen`             |
| small  | 2 million           | adjective + noun         | `red_queen`         |
| medium | 2 billion       | adjective + noun + verb  | `red_queen_bomb`  |
| large  | 624 billion     | adjective + noun + verb + adverb | `red_queen_bomb_carefully` |
| huge   | 623 trillion | number + adjective + noun + verb + adverb | `371_red_queen_bomb_carefully` |

## License

MIT
