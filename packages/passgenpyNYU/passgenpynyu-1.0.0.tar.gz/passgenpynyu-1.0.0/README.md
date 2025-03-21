![GitHub Workflow Status](https://github.com/software-students-spring2025/3-python-package-ejsm/actions/workflows/build.yaml/badge.svg?branch=main)

# Password Generator

Our python package provides various password generation and manipulation functions, including a fun password generator that creates hilarious word combinations.

## Pypi Website: [Link](https://pypi.org/project/passgenpyNYU/)

## Installation

To install the package into your virutal environment: 

```bash
pipenv install passgenpyNYU
```

To activate your virtual environment: 

```bash
pipenv shell
```

To exit your virtual environment: 

```bash
exit
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

## How to Contribute: 

Clone the git repository into your local repository using the following command:

```bash
git clone https://github.com/software-students-spring2025/3-python-package-ejsm.git
```

To execute any of the following steps, first navigate to the project directory: 

```bash
cd [path to project directory]
```

To set up the virtual environment, you must first download pipenv: 

```bash
pip install pipenv
```

Next, use the following command to activate the virtual environment:

```bash
pipenv shell
```

If you want to install dependencies into your virtual environment:

```bash
pipenv install [name of package]
```

To build the package, you must first activate the virtual environment and then build: 

```bash
pipenv shell
python3 -m build
```

To test the package, you must first activate the virtual environment and then test using pytest: 

```bash
pipenv shell
python3 -m pytest
```

There are already 35 different tests cases that can found in tests/test_core.py. 

To make contributes, you must first create a new branch, switch to that branch, commit that branch to the git repository and make a Pull Request on git: 

```bash
git branch [branch name]
git checkout [branch name]
git add [file]
git commit -m "commit message"
git push origin [branch name]
```

## Contributors: 

Jeffrey Chen - [Github Link](https://github.com/JeffreyChen112)

Shaurya Srivastava - [Github Link](https://github.com/shauryasr04)

Ethan Zheng - [Github Link](https://github.com/ez2146)

Max Meyring - [Github Link](https://github.com/maxlmeyring)
