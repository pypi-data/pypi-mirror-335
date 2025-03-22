# 30 Days of PyAI Helpers

A collection of helper functions designed to support the *30 Days of AI with Python* course by Witeout Codes. This library provides utilities to streamline coding tasks, including colorful terminal output with `colorama`.

## Installation

Install the package via PyPI:

```bash
pip install 30-days-of-pyai-helpers
```


## Usage
Here’s an example of using the helper functions (assuming print_helpers.py contains slow_print, etc.):

```python
from _30_days_of_pyai_helpers.print_helpers import slow_print, slow_print_header, slow_print_error

# Print text slowly with color
slow_print("Processing AI task...")
slow_print_header("Day 1: Introduction to AI")
slow_print_error("Error: Missing input data")
```