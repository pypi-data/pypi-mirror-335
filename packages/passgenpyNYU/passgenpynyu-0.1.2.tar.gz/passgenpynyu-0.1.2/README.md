![GitHub Workflow Status](https://github.com/software-students-spring2025/3-python-package-ejsm/actions/workflows/build.yaml/badge.svg?branch=main)

# Password Generator

Our python package provides various password generation and manipulation functions, including a fun password generator that creates hilarious word combinations.

## Installation

To install the package into your virutal environment: 

```bash
pipenv install passgenpyNYU
```

To activate your virtual environment: 

```bash
pipenv shell
```

To run the package from the terminal:

```bash
python3 -m passgenpyNYU -g 10
```

The above calls the generate function to generate a random password of length 10. Use "python3 -m passgenpyNYU -h" to see all available terminal commands. 

## Features / Running the package in your own code

The package provides several functions for password generation and manipulation:

### 1. `generate(length, capitalize=False, numbers=False, symbols=False)`
Generates a random password with specified characteristics.

Parameters:
- `length` (int): The desired length of the password
- `capitalize` (bool, optional): Whether to include uppercase letters (default: False)
- `numbers` (bool, optional): Whether to include numbers (default: False)
- `symbols` (bool, optional): Whether to include special symbols (default: False)

Example:
```python
from passgenpyNYU import core as cd

# Generate a simple 8-character password
password = cd.generate(8)

# Generate a complex 12-character password with all options
complex_password = cd.generate(12, capitalize=True, numbers=True, symbols=True)
```

### 2. `caesar_cipher(word, shift)`
Applies a Caesar cipher to the input string.

Parameters:
- `word` (str): The text to encrypt
- `shift` (int): The shift value (must be between 1 and 25)

Example:
```python
from passgenpyNYU import core as cd

encrypted = cd.caesar_cipher("Hello", 3)
```

### 3. `scramble(string)`
Randomly scrambles the characters in the input string.

Parameters:
- `string` (str): The text to scramble

Example:
```python
from passgenpyNYU import core as cd

scrambled = cd.scramble("Hello World")
```

### 4. `binary_password(length)`
Generates a random binary password of specified length.

Parameters:
- `length` (int): The desired length of the binary password

Example:
```python
from passgenpyNYU import core as cd

binary = cd.binary_password(8)
```

### 5. `generateHash(password)`
Generates a SHA-256 hash of the input password.

Parameters:
- `password` (str): The password to hash

Example:
```python
from passgenpyNYU import core as cd

hashed = cd.generateHash("myPassword123")
```

### 6. `getFunnyPassword()`
Generates a funny password by combining random words from predefined lists.

Example:
```python
from passgenpyNYU import core as cd

funny_pass = cd.getFunnyPassword()
```
### Link to Example code: [example.py](example.py)
