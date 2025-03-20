# Enhancement

A collection of Python utilities and enhancements for better development experience.

## Installation

```bash
pip install enhancement
```

## Features

This package provides several utility modules to enhance your Python development experience:

- `cache_result`: Caching utilities for function results
- `iterable`: Enhanced iterable operations
- `timeit`: Timing utilities for performance measurement
- `ndict`: Enhanced dictionary operations
- `singleton`: Singleton pattern implementation
- `safe_get`: Safe attribute and item access utilities

## Usage

### Cache Result

```python
from enhancement.cache_result import cache_result

@cache_result
def expensive_computation(x):
    # Result will be cached
    return x ** 2
```

### Timing Utilities

```python
from enhancement.timeit import timeit

@timeit
def my_function():
    # Function execution time will be measured
    pass
```

### Safe Get

```python
from enhancement.safe_get import safe_get

data = {"a": {"b": {"c": 1}}}
value = safe_get(data, "a.b.c")  # Returns 1
value = safe_get(data, "a.b.d")  # Returns None
```

## Requirements

- Python 3.11+
- exchange-calendars >= 4.10

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Harry Zhang (HarryZhang0415@gmail.com)
