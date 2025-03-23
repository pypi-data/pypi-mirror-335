# Pyon

**Pyon (Python Object Notation)** is a serialization/deserialization library that extends JSON to natively support complex Python types. It aims to provide a robust and efficient solution for advanced scenarios like Artificial Intelligence, Machine Learning, and heterogeneous data manipulation.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Simplified Interface](#2-simplified-interface)
3. [Supported Types](#3-supported-types)
4. [Installation](#4-installation)
5. [Quick Start](#5-quick-start)
6. [Examples](#6-examples)
7. [Recursion in Encoding and Decoding](#7-recursion-in-encoding-and-decoding)
8. [Project Structure](#8-project-structure)
9. [Encoders](#9-encoders)
10. [Testing](#10-testing)
11. [Roadmap](#11-roadmap)
12. [Additional Documentation](#12-additional-documentation)
13. [Contributing](#13-contributing)
14. [About the Creator](#14-about-the-creator)
15. [License](#15-license)

---

## 1. Overview

Pyon is built on top of JSON, but goes beyond standard JSON encoding a wide range of Python-specific data types. \
Whether you are working with typical Python containers, specialized data structures for AI/ML, or custom classes, Pyon aims to seamlessly serialize and deserialize them.

Key goals include:

- **Robustness**: Proper handling of complex or custom Python objects.  
- **Efficiency**: Designed for data-intensive applications such as ML or large-scale data pipelines.  
- **Extensibility**: Future reliases will add support for new data types.

---
<br>

## 2. Simplified Interface

Pyon provides a straightforward interface with four main methods:

- **`encode(obj)`**: Serialize a Python object into a Pyon string.

- **`decode(data)`**: Deserialize a Pyon string into the corresponding Python object.

- **`to_file(obj, file_path)`**: Serialize a Python object and save the resulting data to a file.

- **`from_file(file_path)`**: Load data from a file and deserialize it into the corresponding Python object.

Each of these methods automatically detects the data type and applies the appropriate serialization or deserialization logic.

---
<br>

## 3. Supported Types

Pyon supports a broad array of Python types out-of-the-box:
<br/>

**1. Base Types**
- `bool`, `float`, `int`, `str`, `None`

**2. Numeric Types**
- `complex`, `decimal.Decimal`

**3. Collection Types**
- `bytearray`, `bytes`, `frozenset`, `list`, `set`, `tuple`
- `ChainMap`, `Counter`, `defaultdict`, `deque`, `namedtuple` (collections)

**4. Datetime Types**
- `datetime.date`, `datetime.datetime`, `datetime.time`

**5. Mapping Types**
- `class` (user defined classes), `dataclasses.dataclass`, `dict`, `Enum`

**6. Specialized Types**
- `bitarray.bitarray`, `numpy.ndarray`, `pandas.DataFrame`, `pyon.File`, `uuid.UUID`

---
<br>

## 4. Installation

Pyon is planned to be released on PyPI. Once available, you can install it via:

```bash
pip install pyon-core
```

If the package is not yet on PyPI, you can install directly from the source:

```bash
pip install git+https://github.com/eonflux-ai/pyon.git
```

*The package 'pion-core' is engine behind the upcoming Pyon ecosystem. If the original PyPI package 'pyon' is released, this package will become its foundation.*

---
<br>

## 5. Quick Start

Below are some quick examples to help you get started.

### Basic Serialization and Deserialization

```python
import pyon

# 1. Python Data: Classes, Collections, Dataframes, Numpy arrays, etc...
data = {...}

# 2. One line Encode and Decode...
encoded = pyon.encode(data)
decoded = pyon.decode(encoded)

# 3. One line Encode and Decode to and from File...
pyon.to_file(data, "data.pyon")
decoded = pyon.from_file("data.pyon")
```

---
<br>

## 6. Examples

Pyon includes a wide set of examples to demonstrate its capabilities in handling different data types and scenarios.  
These examples are located in the `examples/` directory and provide practical use cases for serialization and deserialization.

Check **[EXAMPLES.md](examples/EXAMPLES.md)** for more information.

---
<br>

## 7. Recursion in Encoding and Decoding (Nested Types)

Pyon excels at handling recursive data structures seamlessly. Whether your data includes deeply nested dictionaries, lists, or custom objects, Pyon ensures accurate serialization and deserialization across all levels.

```python
import pyon

# 1. Test Objects...
example_data = {

    # 1.1 Tuple, Set...
    "tuple-set": ({"abc", "def"}),

    # 1.2 List, Tuple, Set...
    "list-tuple-set": [({"abc", "def"}), ({1, 2}), ({True, False})],

    # 1.3 Dict, List, Tuple, Set...
    "dict-list-tuple-set": {
        "a": [({"abc", "def"}), ({1, 2}), ({True, False})]
    },

    # 1.4 Dict, Dict, List, Tuple, Set...
    "dict-dict-list-tuple-set": {
        "one": {"a": [({"abc", "def"}), ({1, 2}), ({True, False})]},
        "two": {"b": [({"ghi", "jkl"}), ({3.0, 4.0}), ({True, False})]}
    }

}

# 2. One Line encode and decode...
encoded = pyon.encode(example_data)
decoded = pyon.decode(encoded)
```

Pyon's recursive encoding and decoding provide a reliable way to handle arbitrarily complex structures, making it ideal for advanced use cases like configuration management, AI/ML pipelines, or hierarchical datasets.

Check **[EXAMPLES.md](examples/EXAMPLES.md)** for more information.

---
<br>

## 8. Project Structure

Here’s the project structure for Pyon:

```
Pyon/
├── LICENSE                         	    # License details
├── README.md                       	    # Project overview and instructions
├── setup.py                        	    # Build and packaging configuration
├── pyon/                           	    # Main source code
│   ├── __init__.py                 	    # Package initialization
│   ├── api.py                      	    # Public API for encoding/decoding
│   ├── encoder.py                  	    # Public interface for encoding logic
│   ├── encoders/                   	    # Submodules for encoding specific data types
│   │   ├── __init__.py             	    # Initialization of the encoders package
│   │   ├── base_types.py           	    # Encoding/decoding for base types
│   │   ├── numeric_types.py        	    # Encoding/decoding for numeric types
│   │   ├── collection_types.py     	    # Encoding/decoding for collections
│   │   ├── datetime_types.py       	    # Encoding/decoding for datetime types
│   │   ├── specialized_types.py    	    # Encoding/decoding for specialized types
│   │   ├── mapping_types.py        	    # Encoding/decoding for key-value types
│   ├── file.py                     	    # File-related utilities
│   ├── supported_types.py          	    # Definitions of supported types and constants
│   ├── utils.py                    	    # General helper functions
├── tests/                          	    # Tests for the project
│   ├── __init__.py                 	    # Test package initialization
│   ├── test_api.py                 	    # Tests for the API module
│   ├── test_encoder/               	    # Tests for encoding submodules
│   │   ├── test_base_types.py      	    # Tests for base types encoding
│   │   ├── test_numeric_types.py   	    # Tests for numeric types encoding
│   │   ├── test_collection_types.py	    # Tests for collections encoding
│   │   ├── test_datetime_types.py  	    # Tests for datetime types encoding
│   │   ├── test_specialized_types.py	    # Tests for specialized types encoding
│   │   ├── test_mapping_types.py   	    # Tests for key-value types encoding
│   ├── test_file.py                	    # Tests for file utilities
│   ├── test_supported_types.py     	    # Tests for supported types and constants
│   ├── test_utils.py               	    # Tests for general utilities
├── docs/                           	    # Documentation
│   ├── ROADMAP.md                  	    # Development roadmap
│   ├── TASKS.md                    	    # Task breakdown by version
│   ├── VERSION.md                  	    # Version details and changelog
```

---

### **Key Highlights**

1. **Public Interface**:

   - The `api.py` file provides a high-level interface for users, exposing key methods like `encode`, `decode`, `to_file`, and `from_file` for seamless serialization and deserialization.

   - The `encoder.py` file in the root directory serves as the public interface for encoding/decoding logic, while the internal logic is delegated to submodules in `encoders/`.

2. **Encoders Modularization**:

   - The `encoders/` directory contains submodules for handling specific types of data (e.g., basic types, collections, numeric types).
   - This improves scalability and separates the encoding logic from the main `encoder.py` file.

3. **Testing Structure**:

   - The `tests/` directory mirrors the project’s modular structure, with subtests for each encoder submodule.

This structure ensures clarity, scalability, and ease of maintenance as the project evolves. If you have any questions or suggestions, feel free to contribute!

---
<br>

## 9. Encoders

The **encoders** in Pyon are modularized to handle different data types efficiently. The main `encoder.py` file serves as the public interface for encoding and decoding, while the internal logic is organized into submodules within the `encoders/` directory.

Each submodule is responsible for specific categories of data types, ensuring maintainability and scalability. Below is an overview of the encoders and the types they manage:


| **Encoder**         | **Types**                                                                               |
|---------------------|-----------------------------------------------------------------------------------------|
| `base_types`        | `bool`, `float`, `int`, `str`, `None`                                                   |
| `numeric_types`     | `complex`, `decimal.Decimal`                                                            |
| `collection_types`  | `bytearray`, `bytes`, `frozenset`, `list`, `set`, `tuple`                               |
|                     | `ChainMap`, `Counter`, `defaultdict`, `deque`, `namedtuple` (from collections)          |
| `datetime_types`    | `datetime.date`, `datetime.datetime`, `datetime.time`                                   |
| `mapping_types`     | `class` (user defined classes), `dataclasses.dataclass`, `dict`, `Enum`                 |
| `specialized_types` | `bitarray.bitarray`, `numpy.ndarray`, `pandas.DataFrame`, `pyon.File`, `uuid.UUID`      |


This modularization simplifies the process of adding support for new data types and ensures that each encoder submodule focuses solely on its designated category of data.

As the building blocks for other types, the base types don't require encoding and decoding.

---
<br>

## 10. Testing

Pyon uses **pytest** for automated testing. The test suite covers:

- Serialization and deserialization for all supported types.  
- Validation of valid, invalid, and null inputs.  
- Logging of errors with `caplog` and temporary file handling with `tmp_path`.

To run the tests locally:

```bash
cd Pyon
pytest
```

---
<br>

## 11. Roadmap

For detailed plans, phased expansions, and future directions, see the [ROADMAP.md](docs/ROADMAP.md) file.

---
<br>

## 12. Additional Documentation

- [ROADMAP.md](docs/ROADMAP.md): Detailed plans and future directions for Pyon.  
- [VERSION.md](docs/VERSION.md): Current version details and key features.  
- [TASKS.md](docs/TASKS.md): Progress tracking and specific tasks for each version.

---
<br>

## 13. Contributing

We will welcome contributions of all kinds:

- **Issues**: Report bugs or suggest enhancements via GitHub issues.  
- **Pull Requests**: Submit patches or new features.  
- **Feedback**: Share your use cases to help guide future development.

Please check our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---
<br>

## 14. About the Creator

Eduardo Rodrigues is the visionary behind **Pyon**. As a seasoned developer and project manager, he blends deep technical expertise with a passion for creating scalable and innovative solutions. His journey spans a variety of domains, from public sector innovation to advanced AI research.

### A Passion for Problem-Solving
Eduardo's development philosophy revolves around simplicity, efficiency, and extensibility. His work often bridges the gap between theory and application, as seen in Pyon's ability to handle complex Python types with ease. Eduardo believes in empowering developers to tackle intricate data scenarios through tools that are both robust and user-friendly.

### Innovator in AI and Beyond
Beyond Pyon, Eduardo has spearheaded projects in Artificial Intelligence, such as integrating generative AI to improve knowledge management in government systems. His expertise lies in architecting solutions that merge cutting-edge technology with practical needs, ensuring both performance and reliability.

### Driven by a Larger Vision
Eduardo envisions **Pyon** as more than a library—it’s a stepping stone toward redefining data serialization in Python. His ultimate goal is to drive innovation through open-source projects, fostering collaboration and pushing boundaries in software development.

For questions, collaborations, or contributions, Eduardo invites you to join the journey on GitHub or email him at:
`eduardo@eonflux.ai`

---
<br>

## 15. License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

---
<br>

**Thank you for using Pyon!** 

If you have any questions or suggestions, feel free to open an issue or start a discussion on our GitHub repository.
