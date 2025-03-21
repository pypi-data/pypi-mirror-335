# czipdec

`czipdec` is a Python package for decrypting data, using the C implementation of ZIP data decryption.

## Features

- Provides efficient ZIP data decryption functionality, based on C implementation.
- Supports Python 3.6+

## Installation

Install the latest version of `czipdec` from PyPI:

```bash
pip install czipdec
```

## Usage
Here's how to use `czipdec` for decryption:

```python
import czipdec

password = b'...your encryption password...'
data = b'...your encrypted data...'

dec = czipdec.decrypt(password, data)
