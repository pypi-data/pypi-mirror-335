# wgl

wgl is a Python package that generates random real-world WebGL fingerprint data. This package can be useful for testing, simulations, or generating sample data for WebGL-related projects.

## Features

- Generates a random WebGL vendor.
- Generates a random WebGL renderer.
- Generates a random WebGL version (e.g., WebGL 1.0 or WebGL 2.0).
- Generates a random selection of WebGL extensions.

## Installation

You can install the package using pip:

```bash
pip install wgl
```

## Usage

Below is an example of how to use the package as a whole along with demonstrations of each individual function.

### Full Fingerprint Example

```python
from wgl import full_fingerprint

# Generate a random WebGL fingerprint
fingerprint = full_fingerprint()
print("Random fingerprint:", fingerprint)
```

The output will be a dictionary with the following keys:
- `vendor`: A random WebGL vendor (e.g., "Intel", "NVIDIA").
- `renderer`: A random WebGL renderer.
- `version`: A random WebGL version (e.g., "WebGL 1.0" or "WebGL 2.0").
- `extensions`: A list of randomly selected WebGL extensions.

### Individual Function Examples

```python
from wgl import get_vendor, get_renderer, get_version, get_extensions

# Get a random WebGL vendor
vendor = get_vendor()
print("Vendor:", vendor)

# Get a random WebGL renderer
renderer = get_renderer()
print("Renderer:", renderer)

# Get a random WebGL version
version = get_version()
print("Version:", version)

# Get a random selection of WebGL extensions
extensions = get_extensions()
print("Extensions:", extensions)
```

These examples demonstrate how to access each part of the fingerprint individually.

## Detailed API

The package consists of the following functions:

### get_vendor()
- **Description:**  
  Returns a random WebGL vendor from a predefined list.
- **Returns:**  
  *String* - A vendor name such as "Intel", "NVIDIA", etc.

### get_renderer()
- **Description:**  
  Returns a random WebGL renderer from a comprehensive list of real-world renderer strings.
- **Returns:**  
  *String* - A renderer name selected at random.

### get_version()
- **Description:**  
  Returns a random valid WebGL version string.
- **Returns:**  
  *String* - Either "WebGL 1.0" or "WebGL 2.0", chosen at random.

### get_extensions()
- **Description:**  
  Returns a random selection of one or more WebGL extensions from a predefined list. The number of extensions selected is random.
- **Returns:**  
  *List* - A list of WebGL extension strings (e.g., "EXT_texture_filter_anisotropic", "OES_texture_float", etc.).

### full_fingerprint()
- **Description:**  
  Combines the outputs of `get_vendor()`, `get_renderer()`, `get_version()`, and `get_extensions()` into a single fingerprint dictionary.
- **Returns:**  
  *Dictionary* - A dictionary with keys:
  - `vendor`
  - `renderer`
  - `version`
  - `extensions`

## License

This project is licensed under the MIT License.