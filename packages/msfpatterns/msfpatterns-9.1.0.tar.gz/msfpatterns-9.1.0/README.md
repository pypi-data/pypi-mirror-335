# msfpatterns

[![📦️ PyPI](https://img.shields.io/pypi/v/msfpatterns)](https://pypi.org/project/msfpatterns/) [![👷 Continuous Integration](https://github.com/wrboyce/msfpatterns/actions/workflows/ci.yaml/badge.svg)](https://github.com/wrboyce/msfpatterns/actions/workflows/ci.yaml) [![🧪 Coverage](https://codecov.io/gh/wrboyce/msfpatterns/graph/badge.svg?token=QG683U5IKA)](https://codecov.io/gh/wrboyce/msfpatterns)

`msfpatterns` (Buffer Overflow Finder) is a tool for generating and analyzing cyclic patterns, similar to pattern_create and pattern_offset from Metasploit. It helps exploit developers identify exact buffer overflow offsets across multiple architectures, including 16-bit, 32-bit, and 64-bit platforms.

## Features

- Generate unique cyclic patterns for buffer overflow analysis
- Find offsets of overwritten return addresses in memory dumps
- Supports 2-byte, 4-byte, and 8-byte searches (suitable for MSP430, x86, x86-64, etc.)
- Returns all matching offsets (useful for 16-bit systems where repeats may occur)
- Simple CLI interface

## Installation

### Using uv (recommended)

```bash
uv tool install msfpatterns
```

### Using pip

```bash
pip install msfpatterns
```

## CLI Usage

### Generating a Pattern

```bash
pattern 128 # Generates a pattern of length 128
```

### Finding an Offset

```bash
pattern -q 0x41306241 128 # Find offset of 0x41306241 in a 128-byte pattern
```

## Library Usage

You can also use msfpatterns as a Python library:

```python
from msfpatterns import generate_pattern, find_offset

pattern = generate_pattern(128)
print(pattern)
offset = find_offset("0x41306241", 128)
print(f"Offset: {offset}")
```
